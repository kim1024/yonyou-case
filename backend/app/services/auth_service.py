import hashlib
import logging
from datetime import datetime, timedelta, timezone

from jose import JWTError, jwt
from passlib.context import CryptContext

from app.config import settings

_logger = logging.getLogger(__name__)

# bcrypt 密码哈希上下文
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# JWT 配置
_base_secret = settings.get("admin", {}).get("jwt_secret")
_INSECURE_DEFAULTS = {"default-secret-change-me", "change-me-in-production"}
if not _base_secret or _base_secret in _INSECURE_DEFAULTS:
    raise RuntimeError(
        "jwt_secret is not configured or is using an insecure default value. "
        "Set a strong, unique jwt_secret in config.yaml under admin.jwt_secret. "
        "Without this, anyone can forge authentication tokens."
    )

# 基于配置密钥派生 JWT 签名密钥（多进程/重启保持一致）
SECRET_KEY = hashlib.sha256(_base_secret.encode()).hexdigest()
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_HOURS = settings.admin.token_expire_hours


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """验证明文密码与哈希是否匹配。"""
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """生成密码的 bcrypt 哈希。"""
    return pwd_context.hash(password)


def create_access_token(data: dict) -> str:
    """创建 JWT token，过期时间由 admin.token_expire_hours 配置（默认4小时）。"""
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(hours=ACCESS_TOKEN_EXPIRE_HOURS)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def verify_token(token: str) -> dict:
    """解码 JWT token，返回 payload；无效时抛出 JWTError。"""
    return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
