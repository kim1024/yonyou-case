"""LLM fallback chain management API endpoints."""

import logging
import uuid
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel, ConfigDict, Field, model_validator
from typing import Optional, List

from app.database import get_db
from app.models.llm_config import LLMConfig
from app.models.model_fallback_setting import ModelFallbackSetting
from app.dependencies import get_current_user
from app.services.llm_runtime import deactivate_all_configs
from app.services.token_quota_service import get_effective_quota
from app.utils.datetime import utc_isoformat
from app.routers.admin_llm import mask_api_key

router = APIRouter(prefix="/api/admin/llm-chains", tags=["llm-chains"])

_logger = logging.getLogger(__name__)


# ─── Pydantic Models ──────────────────────────────────────────────────────


class ChainCreate(BaseModel):
    model_config = ConfigDict(extra="ignore")

    primary_config_id: int
    fallback_config_ids: List[int] = []
    failure_threshold: int = Field(default=3, ge=1)
    timeout_seconds: int = Field(default=30, ge=1)
    cooldown_seconds: int = Field(default=300, ge=0)

    @model_validator(mode="before")
    @classmethod
    def normalize_timeout_field(cls, data):
        if isinstance(data, dict) and "timeout_seconds" not in data and "timeout_threshold" in data:
            data["timeout_seconds"] = data["timeout_threshold"]
        return data


class ChainUpdate(BaseModel):
    model_config = ConfigDict(extra="ignore")

    failure_threshold: Optional[int] = Field(default=None, ge=1)
    timeout_seconds: Optional[int] = Field(default=None, ge=1)
    cooldown_seconds: Optional[int] = Field(default=None, ge=0)
    fallback_config_ids: Optional[List[int]] = None

    @model_validator(mode="before")
    @classmethod
    def normalize_timeout_field(cls, data):
        if isinstance(data, dict) and "timeout_seconds" not in data and "timeout_threshold" in data:
            data["timeout_seconds"] = data["timeout_threshold"]
        return data


class AddFallback(BaseModel):
    config_id: int


class ReorderFallbacks(BaseModel):
    config_ids: List[int]


# ─── Helpers ──────────────────────────────────────────────────────────────


def _config_dict(c: LLMConfig) -> dict:
    """Serialize an LLMConfig with masked API key."""
    return {
        "id": c.id,
        "name": c.name,
        "api_base_url": c.api_base_url,
        "api_key_masked": mask_api_key(c.api_key),
        "model": c.model,
        "temperature": c.temperature,
        "max_tokens": c.max_tokens,
        "timeout": c.timeout,
        "is_active": c.is_active,
        "role": c.role,
        "fallback_order": c.fallback_order,
        "fallback_group_id": c.fallback_group_id,
        "daily_token_quota": c.daily_token_quota,
    }


def _chain_dict(setting: ModelFallbackSetting, primary: LLMConfig, fallbacks: List[LLMConfig], db: Session = None) -> dict:
    """Build the full chain response dict."""
    # 限额信息（链路级别，取主模型的限额，统计链路总用量）
    quota_info = None
    if db is not None:
        quota = get_effective_quota(db, primary.id)
        quota_info = {
            "limit": quota["limit"],
            "used": quota["used"],
            "remaining": quota["remaining"],
        }
    return {
        "id": setting.id,
        "primary_config_id": primary.id,
        "primary_config": _config_dict(primary),
        "fallbacks": [
            {"config_id": f.id, "order": f.fallback_order, "config": _config_dict(f)}
            for f in sorted(fallbacks, key=lambda x: x.fallback_order)
        ],
        "failure_threshold": setting.failure_threshold,
        "timeout_seconds": setting.timeout_seconds,
        "timeout_threshold": setting.timeout_seconds,
        "cooldown_seconds": setting.cooldown_seconds,
        "created_at": utc_isoformat(setting.created_at),
        "updated_at": utc_isoformat(setting.updated_at),
        "quota_info": quota_info,
    }


def _dissolve_config(config: LLMConfig) -> None:
    """Reset a config back to standalone."""
    config.role = "standalone"
    config.fallback_order = 0
    config.fallback_group_id = None
    config.is_active = False


# ─── 1. List all chains ───────────────────────────────────────────────────


@router.get("/")
def list_chains(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """List all LLM fallback chains."""
    fallback_settings = db.query(ModelFallbackSetting).all()
    chains = []
    cleaned = False
    for s in fallback_settings:
        primary = db.query(LLMConfig).filter(LLMConfig.id == s.primary_llm_config_id).first()
        if not primary:
            _logger.warning("Orphaned ModelFallbackSetting id=%s, primary_llm_config_id=%s - deleting", s.id, s.primary_llm_config_id)
            db.delete(s)
            cleaned = True
            continue
        fallbacks = (
            db.query(LLMConfig)
            .filter(
                LLMConfig.fallback_group_id == primary.fallback_group_id,
                LLMConfig.id != primary.id,
            )
            .all()
        )
        chains.append(_chain_dict(s, primary, fallbacks, db))
    if cleaned:
        db.commit()
    return {"chains": chains}


# ─── 1b. Get chain runtime status ────────────────────────────────────────


@router.get("/{chain_id}/status")
def get_chain_status(
    chain_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """Return the runtime status of a fallback chain (active model, failure counts, cooldown state)."""
    setting = db.query(ModelFallbackSetting).filter(ModelFallbackSetting.id == chain_id).first()
    if not setting:
        raise HTTPException(status_code=404, detail="降级链不存在")
    primary = db.query(LLMConfig).filter(LLMConfig.id == setting.primary_llm_config_id).first()
    if not primary or not primary.fallback_group_id:
        raise HTTPException(status_code=404, detail="主配置异常")

    from app.services.llm_chain_manager import get_chain_manager

    status = get_chain_manager().get_chain_status(primary.fallback_group_id)
    return status


# ─── 2. Get single chain ─────────────────────────────────────────────────


@router.get("/{chain_id}")
def get_chain(
    chain_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """Get a single LLM fallback chain by ID."""
    setting = db.query(ModelFallbackSetting).filter(ModelFallbackSetting.id == chain_id).first()
    if not setting:
        raise HTTPException(status_code=404, detail="降级链不存在")
    primary = db.query(LLMConfig).filter(LLMConfig.id == setting.primary_llm_config_id).first()
    if not primary:
        raise HTTPException(status_code=404, detail="主配置不存在")
    fallbacks = (
        db.query(LLMConfig)
        .filter(
            LLMConfig.fallback_group_id == primary.fallback_group_id,
            LLMConfig.id != primary.id,
        )
        .all()
    )
    return _chain_dict(setting, primary, fallbacks, db)


# ─── 3. Create chain ─────────────────────────────────────────────────────


@router.post("/")
def create_chain(
    data: ChainCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """Create a new LLM fallback chain."""
    if len(data.fallback_config_ids) < 1:
        raise HTTPException(status_code=400, detail="调用链路至少需要 2 个模型，请至少选择 1 个备用模型")

    primary = db.query(LLMConfig).filter(LLMConfig.id == data.primary_config_id).first()
    if not primary:
        raise HTTPException(status_code=400, detail=f"主配置 {data.primary_config_id} 不存在")
    if primary.role != "standalone":
        raise HTTPException(status_code=400, detail="主配置已属于某条降级链，不能再次使用")

    # Validate all fallback configs
    fallbacks = []
    seen_fallback_ids: set[int] = set()
    for fid in data.fallback_config_ids:
        if fid in seen_fallback_ids:
            raise HTTPException(status_code=400, detail=f"备用配置 {fid} 重复")
        seen_fallback_ids.add(fid)
        cfg = db.query(LLMConfig).filter(LLMConfig.id == fid).first()
        if not cfg:
            raise HTTPException(status_code=400, detail=f"备用配置 {fid} 不存在")
        if cfg.role != "standalone":
            raise HTTPException(status_code=400, detail=f"备用配置 {fid} 已属于某条降级链")
        if fid == data.primary_config_id:
            raise HTTPException(status_code=400, detail="主配置不能同时作为备用配置")
        fallbacks.append(cfg)

    group_id = uuid.uuid4().hex[:12]

    deactivate_all_configs(db)

    # Update primary
    primary.role = "primary"
    primary.fallback_order = 0
    primary.fallback_group_id = group_id
    primary.is_active = True

    # Update fallbacks
    for i, cfg in enumerate(fallbacks, start=1):
        cfg.role = "fallback"
        cfg.fallback_order = i
        cfg.fallback_group_id = group_id
        cfg.is_active = False

    # Create threshold setting
    setting = ModelFallbackSetting(
        primary_llm_config_id=primary.id,
        failure_threshold=data.failure_threshold,
        timeout_seconds=data.timeout_seconds,
        cooldown_seconds=data.cooldown_seconds,
    )
    db.add(setting)
    db.commit()
    db.refresh(setting)

    return _chain_dict(setting, primary, fallbacks, db)


# ─── 4. Update chain (thresholds + optional fallback reorder) ─────────────


@router.put("/{chain_id}")
def update_chain(
    chain_id: int,
    data: ChainUpdate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """Update chain thresholds and optionally reorder/add/remove fallbacks."""
    setting = db.query(ModelFallbackSetting).filter(ModelFallbackSetting.id == chain_id).first()
    if not setting:
        raise HTTPException(status_code=404, detail="降级链不存在")

    primary = db.query(LLMConfig).filter(LLMConfig.id == setting.primary_llm_config_id).first()
    if not primary:
        raise HTTPException(status_code=404, detail="主配置不存在")

    # Update thresholds
    if data.failure_threshold is not None:
        setting.failure_threshold = data.failure_threshold
    if data.timeout_seconds is not None:
        setting.timeout_seconds = data.timeout_seconds
    if data.cooldown_seconds is not None:
        setting.cooldown_seconds = data.cooldown_seconds

    # Reorder / add / remove fallbacks if the list is provided
    if data.fallback_config_ids is not None:
        if len(data.fallback_config_ids) < 1:
            raise HTTPException(status_code=400, detail="调用链路至少需要保留 1 个备用模型；如仅保留单模型，请解散链路")

        group_id = primary.fallback_group_id

        # Current fallbacks in this chain
        current_fallbacks = (
            db.query(LLMConfig)
            .filter(
                LLMConfig.fallback_group_id == group_id,
                LLMConfig.id != primary.id,
            )
            .all()
        )
        current_ids = {c.id for c in current_fallbacks}
        active_ids = {c.id for c in current_fallbacks if c.is_active}
        new_ids = set(data.fallback_config_ids)

        # Dissolve configs that are being removed
        to_remove = current_ids - new_ids
        removed_active = False
        for cfg in current_fallbacks:
            if cfg.id in to_remove:
                removed_active = removed_active or cfg.is_active
                _dissolve_config(cfg)

        # Validate and assign new fallbacks
        new_fallbacks = []
        seen_new_ids: set[int] = set()
        for fid in data.fallback_config_ids:
            if fid in seen_new_ids:
                raise HTTPException(status_code=400, detail=f"配置 {fid} 重复")
            seen_new_ids.add(fid)
            cfg = db.query(LLMConfig).filter(LLMConfig.id == fid).first()
            if not cfg:
                raise HTTPException(status_code=400, detail=f"配置 {fid} 不存在")
            if cfg.id == primary.id:
                raise HTTPException(status_code=400, detail="主配置不能作为备用")
            if cfg.id not in current_ids and cfg.role != "standalone":
                raise HTTPException(status_code=400, detail=f"配置 {fid} 已属于另一条降级链")
            new_fallbacks.append(cfg)

        for i, cfg in enumerate(new_fallbacks, start=1):
            cfg.role = "fallback"
            cfg.fallback_order = i
            cfg.fallback_group_id = group_id
            cfg.is_active = cfg.id in active_ids

        has_active_in_group = any(
            cfg.is_active
            for cfg in db.query(LLMConfig).filter(LLMConfig.fallback_group_id == group_id).all()
        )
        if removed_active or not has_active_in_group:
            deactivate_all_configs(db, exclude_config_id=primary.id)
            primary.is_active = True

    db.commit()

    if data.fallback_config_ids is not None and primary.fallback_group_id:
        from app.services.llm_chain_manager import get_chain_manager
        get_chain_manager().reset_chain(primary.fallback_group_id)

    db.refresh(setting)

    fallbacks = (
        db.query(LLMConfig)
        .filter(
            LLMConfig.fallback_group_id == primary.fallback_group_id,
            LLMConfig.id != primary.id,
        )
        .all()
    )
    return _chain_dict(setting, primary, fallbacks, db)


# ─── 5. Delete chain (dissolve) ──────────────────────────────────────────


@router.delete("/{chain_id}")
def delete_chain(
    chain_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """Dissolve a chain: all configs return to standalone, delete the setting row."""
    setting = db.query(ModelFallbackSetting).filter(ModelFallbackSetting.id == chain_id).first()
    if not setting:
        raise HTTPException(status_code=404, detail="降级链不存在")

    primary = db.query(LLMConfig).filter(LLMConfig.id == setting.primary_llm_config_id).first()
    group_id = None

    # Dissolve all configs in the group
    if primary:
        group_id = primary.fallback_group_id
        _dissolve_config(primary)
        deactivate_all_configs(db, exclude_config_id=primary.id)
        primary.is_active = True
        if group_id:
            fallbacks = (
                db.query(LLMConfig)
                .filter(
                    LLMConfig.fallback_group_id == group_id,
                    LLMConfig.id != primary.id,
                )
                .all()
            )
            for fb in fallbacks:
                _dissolve_config(fb)

    db.delete(setting)
    db.commit()

    # Reset chain manager runtime state
    if group_id:
        from app.services.llm_chain_manager import get_chain_manager
        get_chain_manager().reset_chain(group_id)

    return {"message": "降级链已解散"}


# ─── 6. Add single fallback ──────────────────────────────────────────────


@router.post("/{chain_id}/fallbacks")
def add_fallback(
    chain_id: int,
    data: AddFallback,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """Add a single fallback config to a chain."""
    setting = db.query(ModelFallbackSetting).filter(ModelFallbackSetting.id == chain_id).first()
    if not setting:
        raise HTTPException(status_code=404, detail="降级链不存在")

    primary = db.query(LLMConfig).filter(LLMConfig.id == setting.primary_llm_config_id).first()
    if not primary:
        raise HTTPException(status_code=404, detail="主配置不存在")

    if data.config_id == primary.id:
        raise HTTPException(status_code=400, detail="主配置不能作为备用")

    cfg = db.query(LLMConfig).filter(LLMConfig.id == data.config_id).first()
    if not cfg:
        raise HTTPException(status_code=400, detail=f"配置 {data.config_id} 不存在")
    if cfg.role != "standalone":
        raise HTTPException(status_code=400, detail=f"配置 {data.config_id} 已属于某条降级链")

    group_id = primary.fallback_group_id
    current_fallbacks = (
        db.query(LLMConfig)
        .filter(
            LLMConfig.fallback_group_id == group_id,
            LLMConfig.id != primary.id,
        )
        .all()
    )
    max_order = max((f.fallback_order for f in current_fallbacks), default=0)

    cfg.role = "fallback"
    cfg.fallback_order = max_order + 1
    cfg.fallback_group_id = group_id
    cfg.is_active = False
    db.commit()

    return {"message": "已添加备用模型", "config_id": cfg.id, "order": cfg.fallback_order}


# ─── 7. Remove fallback ──────────────────────────────────────────────────


@router.delete("/{chain_id}/fallbacks/{config_id}")
def remove_fallback(
    chain_id: int,
    config_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """Remove a fallback from a chain. Auto-dissolves chain if no fallbacks remain."""
    setting = db.query(ModelFallbackSetting).filter(ModelFallbackSetting.id == chain_id).first()
    if not setting:
        raise HTTPException(status_code=404, detail="降级链不存在")

    primary = db.query(LLMConfig).filter(LLMConfig.id == setting.primary_llm_config_id).first()
    if not primary:
        raise HTTPException(status_code=404, detail="主配置不存在")

    cfg = db.query(LLMConfig).filter(LLMConfig.id == config_id).first()
    if not cfg or cfg.fallback_group_id != primary.fallback_group_id:
        raise HTTPException(status_code=404, detail="该配置不属于此降级链")

    group_id = primary.fallback_group_id
    was_active = cfg.is_active
    _dissolve_config(cfg)

    # Check remaining fallbacks
    remaining = (
        db.query(LLMConfig)
        .filter(
            LLMConfig.fallback_group_id == group_id,
            LLMConfig.id != primary.id,
        )
        .all()
    )

    if not remaining:
        # Auto-dissolve: only primary left
        _dissolve_config(primary)
        deactivate_all_configs(db, exclude_config_id=primary.id)
        primary.is_active = True
        db.delete(setting)
        db.commit()
        from app.services.llm_chain_manager import get_chain_manager
        get_chain_manager().reset_chain(group_id)
        return {"message": "最后一个备用模型已移除，降级链已自动解散"}

    if was_active:
        deactivate_all_configs(db, exclude_config_id=primary.id)
        primary.is_active = True

    # Re-number remaining fallbacks
    remaining.sort(key=lambda x: x.fallback_order)
    for i, fb in enumerate(remaining, start=1):
        fb.fallback_order = i

    db.commit()
    from app.services.llm_chain_manager import get_chain_manager
    get_chain_manager().reset_chain(group_id)
    return {"message": "已移除备用模型"}


# ─── 8. Reorder fallbacks ────────────────────────────────────────────────


@router.put("/{chain_id}/fallbacks/reorder")
def reorder_fallbacks(
    chain_id: int,
    data: ReorderFallbacks,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """Reorder fallbacks within a chain."""
    setting = db.query(ModelFallbackSetting).filter(ModelFallbackSetting.id == chain_id).first()
    if not setting:
        raise HTTPException(status_code=404, detail="降级链不存在")

    primary = db.query(LLMConfig).filter(LLMConfig.id == setting.primary_llm_config_id).first()
    if not primary:
        raise HTTPException(status_code=404, detail="主配置不存在")

    group_id = primary.fallback_group_id
    current_ids = {
        c.id
        for c in db.query(LLMConfig).filter(
            LLMConfig.fallback_group_id == group_id,
            LLMConfig.id != primary.id,
        ).all()
    }

    for fid in data.config_ids:
        if fid not in current_ids:
            raise HTTPException(status_code=400, detail=f"配置 {fid} 不属于此降级链")

    # Check for duplicates
    seen: set = set()
    for fid in data.config_ids:
        if fid in seen:
            raise HTTPException(status_code=400, detail=f"配置 {fid} 重复")
        seen.add(fid)

    # Apply new order
    for i, fid in enumerate(data.config_ids, start=1):
        cfg = db.query(LLMConfig).filter(LLMConfig.id == fid).first()
        cfg.fallback_order = i

    db.commit()
    return {"message": "已重新排序"}
