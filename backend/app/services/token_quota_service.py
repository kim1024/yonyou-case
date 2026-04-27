"""Token daily quota service: tracks and enforces per-model and per-chain daily token limits."""

import logging
from datetime import datetime, timezone, timedelta

from fastapi import HTTPException
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.llm_config import LLMConfig
from app.models.token_usage_log import TokenUsageLog

_logger = logging.getLogger(__name__)

# UTC+8 timezone for daily reset at midnight Beijing time
_CN_TZ = timezone(timedelta(hours=8))


def _today_start_utc8() -> datetime:
    """Return today's midnight in UTC+8, expressed as a UTC-aware datetime."""
    now_cn = datetime.now(_CN_TZ)
    midnight_cn = now_cn.replace(hour=0, minute=0, second=0, microsecond=0)
    return midnight_cn.astimezone(timezone.utc)


def _next_reset_utc8() -> str:
    """Return the next reset time (tomorrow midnight UTC+8) as ISO string."""
    now_cn = datetime.now(_CN_TZ)
    tomorrow_midnight = (now_cn + timedelta(days=1)).replace(hour=0, minute=0, second=0, microsecond=0)
    return tomorrow_midnight.isoformat()


def get_daily_usage_by_config(db: Session, config_id: int) -> int:
    """查询单个 config 当日 token 用量。"""
    today_start = _today_start_utc8()
    row = (
        db.query(func.coalesce(func.sum(TokenUsageLog.total_tokens), 0))
        .filter(
            TokenUsageLog.llm_config_id == config_id,
            TokenUsageLog.request_timestamp >= today_start,
        )
        .scalar()
    )
    return int(row)


def get_daily_usage_by_chain(db: Session, fallback_group_id: str) -> int:
    """查询链路当日总用量（累计所有链路内模型的 token）。

    链路模式下 token 统一记录到主模型的 config_id，因此主要按主模型查询。
    同时兼容旧数据：也查询当前链路内其他 config 的历史用量。
    """
    today_start = _today_start_utc8()

    primary = get_primary_config(db, fallback_group_id)
    if not primary:
        return 0

    # 收集链路内所有 config_id（包含主模型 + 所有备用模型）
    chain_config_ids = [
        c.id for c in
        db.query(LLMConfig.id)
        .filter(LLMConfig.fallback_group_id == fallback_group_id)
        .all()
    ]
    if primary.id not in chain_config_ids:
        chain_config_ids.append(primary.id)

    row = (
        db.query(func.coalesce(func.sum(TokenUsageLog.total_tokens), 0))
        .filter(
            TokenUsageLog.llm_config_id.in_(chain_config_ids),
            TokenUsageLog.request_timestamp >= today_start,
        )
        .scalar()
    )
    return int(row)


def get_primary_config(db: Session, fallback_group_id: str) -> LLMConfig | None:
    """获取链路的主模型配置。"""
    return (
        db.query(LLMConfig)
        .filter(
            LLMConfig.fallback_group_id == fallback_group_id,
            LLMConfig.role == "primary",
        )
        .first()
    )


def get_effective_quota(db: Session, config_id: int) -> dict:
    """获取有效限额信息。

    如果 config 属于链路，取主模型的 daily_token_quota，统计链路总用量。
    如果是 standalone，取自身的 daily_token_quota，统计自身用量。

    返回 {"limit": int, "used": int, "remaining": int, "is_chain": bool}
    """
    config = db.query(LLMConfig).filter(LLMConfig.id == config_id).first()
    if not config:
        return {"limit": 0, "used": 0, "remaining": 0, "is_chain": False}

    if config.fallback_group_id:
        # 链路模式：取主模型的限额
        primary = get_primary_config(db, config.fallback_group_id)
        if primary:
            limit = primary.daily_token_quota
        else:
            limit = config.daily_token_quota
        used = get_daily_usage_by_chain(db, config.fallback_group_id)
        is_chain = True
    else:
        limit = config.daily_token_quota
        used = get_daily_usage_by_config(db, config_id)
        is_chain = False

    remaining = max(0, limit - used) if limit > 0 else -1  # -1 表示不限制
    return {"limit": limit, "used": used, "remaining": remaining, "is_chain": is_chain}


def check_quota(db: Session, config_id: int) -> bool:
    """检查是否还有额度。limit=0 表示不限制，永远返回 True。"""
    quota = get_effective_quota(db, config_id)
    if quota["limit"] <= 0:
        return True
    return quota["remaining"] > 0


def enforce_quota(db: Session, config_id: int) -> None:
    """配额不足时抛出 HTTPException(429)。"""
    quota = get_effective_quota(db, config_id)
    if quota["limit"] > 0 and quota["remaining"] <= 0:
        _logger.warning(
            "Token quota exceeded for config %d: limit=%d, used=%d, remaining=%d",
            config_id, quota["limit"], quota["used"], quota["remaining"],
        )
        raise HTTPException(
            status_code=429,
            detail={
                "code": "TOKEN_QUOTA_EXCEEDED",
                "message": "当日 Token 配额已用完",
                "quota": {
                    "limit": quota["limit"],
                    "used": quota["used"],
                    "remaining": 0,
                    "reset_at": _next_reset_utc8(),
                },
            },
        )
