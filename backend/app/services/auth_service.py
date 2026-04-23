from datetime import datetime, timedelta, timezone

from jose import JWTError, jwt
from passlib.context import CryptContext

from app.config import settings

# bcrypt 密码哈希上下文
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# JWT 配置
_jwt_secret = settings.get("admin", {}).get("jwt_secret")
_INSECURE_DEFAULTS = {"default-secret-change-me", "change-me-in-production"}
if not _jwt_secret or _jwt_secret in _INSECURE_DEFAULTS:
    raise RuntimeError(
        "jwt_secret is not configured or is using an insecure default value. "
        "Set a strong, unique jwt_secret in config.yaml under admin.jwt_secret. "
        "Without this, anyone can forge authentication tokens."
    )
SECRET_KEY = _jwt_secret
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_HOURS = 24


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """验证明文密码与哈希是否匹配。"""
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """生成密码的 bcrypt 哈希。"""
    return pwd_context.hash(password)


def create_access_token(data: dict) -> str:
    """创建 JWT token，24 小时后过期。"""
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(hours=ACCESS_TOKEN_EXPIRE_HOURS)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def verify_token(token: str) -> dict:
    """解码 JWT token，返回 payload；无效时抛出 JWTError。"""
    return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
