"""方案样式主题 CRUD + 版本管理 API。"""

import json
import logging
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import get_current_user
from app.models.plan_theme import PlanTheme
from app.models.plan_theme_version import PlanThemeVersion

_logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/admin/themes", tags=["themes"])

# --- 公开接口（无需鉴权）---

public_router = APIRouter(prefix="/api/themes", tags=["themes"])

# --- 默认样式配置 ---

DEFAULT_STYLE_CONFIG = {
    "accentColor": "#C0392B",
    "highlightColor": "#C0392B",
    "dotColor": "#D4A06A",
    "pricingCardBg": "linear-gradient(135deg, #B83227 0%, #C0392B 35%, #D94A3F 100%)",
    "pricingNumberGradient": "linear-gradient(180deg, #FFE066 0%, #FFD700 40%, #DAA520 100%)",
    "pageBg": "#F8F7F4",
    "cardBg": "#FFFFFF",
    "textColor": "#444444",
    "subtitleColor": "#2D2D2D",
}


# --- 请求体模型 ---


class PlanThemeCreate(BaseModel):
    """新建主题请求体。"""
    name: str
    description: Optional[str] = None
    style_config: Optional[dict] = None


class PlanThemeUpdate(BaseModel):
    """更新主题基本信息请求体。"""
    name: Optional[str] = None
    description: Optional[str] = None


class PlanThemeVersionCreate(BaseModel):
    """创建新版本请求体。"""
    style_config: dict
    remark: Optional[str] = None


# --- 辅助函数 ---


def _serialize_version(v: PlanThemeVersion) -> dict:
    """序列化版本对象。"""
    return {
        "id": v.id,
        "version_number": v.version_number,
        "style_config": json.loads(v.style_config) if v.style_config else None,
        "remark": v.remark,
        "created_by": v.created_by,
        "created_at": v.created_at.isoformat() if v.created_at else None,
    }


# --- 主题 CRUD ---


@router.get("")
def list_themes(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    keyword: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """获取主题列表（分页）。"""
    query = db.query(PlanTheme)

    if keyword:
        query = query.filter(PlanTheme.name.contains(keyword))

    total = query.count()
    items = (
        query
        .order_by(PlanTheme.id.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
        .all()
    )

    result = []
    for t in items:
        current_version_number = None
        if t.current_version_id:
            cv = db.query(PlanThemeVersion).filter(PlanThemeVersion.id == t.current_version_id).first()
            if cv:
                current_version_number = cv.version_number

        result.append({
            "id": t.id,
            "name": t.name,
            "description": t.description,
            "is_active": t.is_active,
            "current_version_id": t.current_version_id,
            "current_version_number": current_version_number,
            "created_at": t.created_at.isoformat() if t.created_at else None,
            "updated_at": t.updated_at.isoformat() if t.updated_at else None,
        })

    return {
        "items": result,
        "total": total,
        "page": page,
        "page_size": page_size,
    }


@router.post("")
def create_theme(
    data: PlanThemeCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """新建主题并创建第一个版本。"""
    theme = PlanTheme(
        name=data.name,
        description=data.description,
        is_active=False,
    )
    db.add(theme)
    db.flush()

    config = data.style_config if data.style_config is not None else DEFAULT_STYLE_CONFIG

    version = PlanThemeVersion(
        theme_id=theme.id,
        version_number=1,
        style_config=json.dumps(config, ensure_ascii=False),
        remark="初始版本",
        created_by=current_user.get("sub"),
    )
    db.add(version)
    db.flush()

    theme.current_version_id = version.id
    db.commit()
    db.refresh(theme)

    return {
        "id": theme.id,
        "version_id": version.id,
        "message": "创建成功",
    }


@router.get("/{theme_id}")
def get_theme(
    theme_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """获取主题详情（含当前版本）。"""
    theme = db.query(PlanTheme).filter(PlanTheme.id == theme_id).first()
    if not theme:
        raise HTTPException(status_code=404, detail="主题不存在")

    current_version = None
    if theme.current_version_id:
        current_version = (
            db.query(PlanThemeVersion)
            .filter(PlanThemeVersion.id == theme.current_version_id)
            .first()
        )

    return {
        "id": theme.id,
        "name": theme.name,
        "description": theme.description,
        "is_active": theme.is_active,
        "current_version_id": theme.current_version_id,
        "created_at": theme.created_at.isoformat() if theme.created_at else None,
        "updated_at": theme.updated_at.isoformat() if theme.updated_at else None,
        "current_version": _serialize_version(current_version) if current_version else None,
    }


@router.put("/{theme_id}")
def update_theme(
    theme_id: int,
    data: PlanThemeUpdate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """更新主题基本信息。"""
    theme = db.query(PlanTheme).filter(PlanTheme.id == theme_id).first()
    if not theme:
        raise HTTPException(status_code=404, detail="主题不存在")

    update_data = data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(theme, key, value)

    db.commit()
    return {"message": "更新成功"}


@router.delete("/{theme_id}")
def delete_theme(
    theme_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """删除主题（级联删除所有版本）。"""
    theme = db.query(PlanTheme).filter(PlanTheme.id == theme_id).first()
    if not theme:
        raise HTTPException(status_code=404, detail="主题不存在")

    if theme.is_active:
        raise HTTPException(status_code=400, detail="激活中的主题不可删除，请先切换激活其他主题")

    db.query(PlanThemeVersion).filter(PlanThemeVersion.theme_id == theme_id).delete()
    db.delete(theme)
    db.commit()

    return {"message": "删除成功"}


# --- 激活操作 ---


@router.post("/{theme_id}/activate")
def activate_theme(
    theme_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """激活主题（将其他所有主题设为非激活）。"""
    theme = db.query(PlanTheme).filter(PlanTheme.id == theme_id).first()
    if not theme:
        raise HTTPException(status_code=404, detail="主题不存在")

    # 确保有版本可激活
    if not theme.current_version_id:
        raise HTTPException(status_code=400, detail="该主题尚未配置版本，无法激活")

    # 将所有主题设为非激活
    db.query(PlanTheme).update({PlanTheme.is_active: False})

    # 激活目标主题
    theme.is_active = True
    db.commit()
    db.refresh(theme)

    return {"message": "激活成功", "is_active": True}


# --- 版本管理 ---


@router.get("/{theme_id}/versions")
def list_versions(
    theme_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """获取版本列表（按版本号倒序）。"""
    theme = db.query(PlanTheme).filter(PlanTheme.id == theme_id).first()
    if not theme:
        raise HTTPException(status_code=404, detail="主题不存在")

    versions = (
        db.query(PlanThemeVersion)
        .filter(PlanThemeVersion.theme_id == theme_id)
        .order_by(PlanThemeVersion.version_number.desc())
        .all()
    )

    return {
        "items": [
            {
                **_serialize_version(v),
                "is_current": v.id == theme.current_version_id,
            }
            for v in versions
        ]
    }


@router.post("/{theme_id}/versions")
def create_version(
    theme_id: int,
    data: PlanThemeVersionCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """创建新版本（自动递增版本号并设为当前版本）。"""
    theme = db.query(PlanTheme).filter(PlanTheme.id == theme_id).first()
    if not theme:
        raise HTTPException(status_code=404, detail="主题不存在")

    max_version = (
        db.query(func.max(PlanThemeVersion.version_number))
        .filter(PlanThemeVersion.theme_id == theme_id)
        .scalar()
    )
    next_version_number = (max_version or 0) + 1

    version = PlanThemeVersion(
        theme_id=theme_id,
        version_number=next_version_number,
        style_config=json.dumps(data.style_config, ensure_ascii=False),
        remark=data.remark,
        created_by=current_user.get("sub"),
    )
    db.add(version)
    db.flush()

    theme.current_version_id = version.id
    db.commit()
    db.refresh(version)

    return {
        "id": version.id,
        "version_number": version.version_number,
        "message": "版本创建成功",
    }


@router.get("/{theme_id}/versions/{version_id}")
def get_version(
    theme_id: int,
    version_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """获取版本详情（完整样式配置）。"""
    version = (
        db.query(PlanThemeVersion)
        .filter(
            PlanThemeVersion.id == version_id,
            PlanThemeVersion.theme_id == theme_id,
        )
        .first()
    )
    if not version:
        raise HTTPException(status_code=404, detail="版本不存在")

    theme = db.query(PlanTheme).filter(PlanTheme.id == theme_id).first()

    return {
        **_serialize_version(version),
        "is_current": theme is not None and version.id == theme.current_version_id,
    }


@router.post("/{theme_id}/versions/{version_id}/rollback")
def rollback_version(
    theme_id: int,
    version_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """回滚到指定版本（将其设为当前版本）。"""
    theme = db.query(PlanTheme).filter(PlanTheme.id == theme_id).first()
    if not theme:
        raise HTTPException(status_code=404, detail="主题不存在")

    version = (
        db.query(PlanThemeVersion)
        .filter(
            PlanThemeVersion.id == version_id,
            PlanThemeVersion.theme_id == theme_id,
        )
        .first()
    )
    if not version:
        raise HTTPException(status_code=404, detail="版本不存在")

    theme.current_version_id = version.id
    db.commit()
    db.refresh(theme)

    return {
        "message": "回滚成功",
        "current_version_id": theme.current_version_id,
        "version_number": version.version_number,
    }


# --- 公开接口 ---


@public_router.get("/active")
def get_active_theme(
    db: Session = Depends(get_db),
):
    """获取当前激活主题的当前版本（无需鉴权）。"""
    theme = (
        db.query(PlanTheme)
        .filter(PlanTheme.is_active == True)  # noqa: E712
        .first()
    )

    if not theme or not theme.current_version_id:
        return None

    version = (
        db.query(PlanThemeVersion)
        .filter(PlanThemeVersion.id == theme.current_version_id)
        .first()
    )
    if not version:
        return None

    return {
        "theme_id": theme.id,
        "name": theme.name,
        "version_id": version.id,
        "version_number": version.version_number,
        "style_config": json.loads(version.style_config) if version.style_config else None,
    }
