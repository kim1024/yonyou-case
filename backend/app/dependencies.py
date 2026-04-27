from fastapi import Depends, HTTPException, Header
from jose import JWTError
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.admin import AdminUser
from app.services.auth_service import verify_token


def get_current_user(
    authorization: str = Header(None),
    db: Session = Depends(get_db),
):
    """从 Authorization 头提取并验证 JWT token，同时确认用户在数据库中仍存在。"""
    if not authorization:
        raise HTTPException(status_code=401, detail="缺少认证信息")

    parts = authorization.split()
    if len(parts) != 2 or parts[0].lower() != "bearer":
        raise HTTPException(status_code=401, detail="认证格式错误")

    try:
        payload = verify_token(parts[1])
    except JWTError:
        raise HTTPException(status_code=401, detail="token无效或已过期")

    # 校验 token 后查询数据库，确认用户仍然存在
    username: str | None = payload.get("sub")
    if not username:
        raise HTTPException(status_code=401, detail="token无效：缺少用户标识")

    user = db.query(AdminUser).filter(AdminUser.username == username).first()
    if user is None:
        raise HTTPException(status_code=401, detail="用户不存在或已被删除")

    return payload
