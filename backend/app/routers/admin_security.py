"""安全设置管理 API。"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field
from app.database import get_db
from app.models.security_setting import SecuritySetting
from app.dependencies import get_current_user
from app.middleware.rate_limit import rate_limit_config

router = APIRouter(prefix="/api/admin/security", tags=["security-settings"])

# 参数校验范围
PARAM_SPECS = {
    "generate_max_requests": {"min": 1, "max": 100, "desc": "每小时最大生成次数（per IP）"},
    "generate_window_seconds": {"min": 60, "max": 86400, "desc": "限流窗口时长（秒）"},
    "generate_cooldown_seconds": {"min": 5, "max": 300, "desc": "请求冷却间隔（秒）"},
    "max_concurrent": {"min": 1, "max": 20, "desc": "最大并发请求数（全局）"},
}


class SecuritySettingUpdate(BaseModel):
    generate_max_requests: int = Field(None, ge=1, le=100)
    generate_window_seconds: int = Field(None, ge=60, le=86400)
    generate_cooldown_seconds: int = Field(None, ge=5, le=300)
    max_concurrent: int = Field(None, ge=1, le=20)


@router.get("/settings")
def list_settings(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """列出所有安全设置。"""
    items = db.query(SecuritySetting).all()
    return {
        "items": [
            {
                "key": s.key,
                "value": int(s.value) if s.value.isdigit() else s.value,
                "description": s.description or "",
            }
            for s in items
        ]
    }


@router.put("/settings")
def update_settings(
    data: SecuritySettingUpdate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """更新安全设置，支持实时生效。"""
    update_data = data.model_dump(exclude_unset=True)
    if not update_data:
        raise HTTPException(status_code=400, detail="没有提供需要更新的配置")

    updated_keys = []
    for key, value in update_data.items():
        setting = db.query(SecuritySetting).filter(SecuritySetting.key == key).first()
        if setting:
            setting.value = str(value)
            updated_keys.append(key)
        else:
            desc = PARAM_SPECS.get(key, {}).get("desc", "")
            db.add(SecuritySetting(key=key, value=str(value), description=desc))
            updated_keys.append(key)

    db.commit()

    # 更新内存缓存，实时生效
    rate_limit_config.update(update_data)

    return {"message": "安全配置已更新，已实时生效", "updated": updated_keys}
