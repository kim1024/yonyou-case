from fastapi import Depends, HTTPException, Header
from jose import JWTError
from app.services.auth_service import verify_token


def get_current_user(authorization: str = Header(None)):
    """从 Authorization 头提取并验证 JWT token。"""
    if not authorization:
        raise HTTPException(status_code=401, detail="缺少认证信息")

    parts = authorization.split()
    if len(parts) != 2 or parts[0].lower() != "bearer":
        raise HTTPException(status_code=401, detail="认证格式错误")

    try:
        payload = verify_token(parts[1])
        return payload
    except JWTError:
        raise HTTPException(status_code=401, detail="token无效或已过期")
