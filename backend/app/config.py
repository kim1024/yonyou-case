import logging
import yaml
from pathlib import Path

_logger = logging.getLogger(__name__)

# 项目根目录：backend/ 的上一级
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
CONFIG_PATH = PROJECT_ROOT / "config.yaml"

DEFAULT_CONFIG = {
    "server": {
        "host": "0.0.0.0",
        "port": 8000,
        "cors_origins": ["http://localhost:5173"],
        "timezone": "",
    },
    "database": {
        "url": "postgresql://postgres:postgres@localhost:5432/yonyou_case",
    },
    "admin": {
        "username": "admin",
        "password": "changeme",
        "jwt_secret": "change-me-in-production",
        "token_expire_hours": 4,
    },
    "llm": {
        "api_key": "sk-xxx",
        "api_base_url": "https://api.openai.com/v1",
        "model": "gpt-4o",
        "temperature": 0.7,
        "max_tokens": 2000,
        "timeout": 60,
    },
    "pricing": {
        "rate_per_hour": 2000,
    },
    "rate_limit": {
        "generate_max_requests": 10,
        "generate_window_seconds": 3600,
        "generate_cooldown_seconds": 30,
        "max_concurrent": 3,
    },
    "frontend": {
        "title": "用友产业案例教学项目课程定制系统",
    },
}


class AdminSettings:
    """管理后台配置段的类型安全访问器。"""

    # token_expire_hours 的有效范围
    _TOKEN_EXPIRE_MIN: int = 1
    _TOKEN_EXPIRE_MAX: int = 720
    _TOKEN_EXPIRE_DEFAULT: int = 4

    def __init__(self, admin_config: dict) -> None:
        self._config = admin_config

    @property
    def token_expire_hours(self) -> int:
        """登录Token过期时间（小时），范围 1-720，默认 4。"""
        raw = self._config.get("token_expire_hours", self._TOKEN_EXPIRE_DEFAULT)
        try:
            value = int(raw)
        except (TypeError, ValueError):
            _logger.warning(
                "admin.token_expire_hours 值无效 (%r)，使用默认值 %d",
                raw, self._TOKEN_EXPIRE_DEFAULT,
            )
            return self._TOKEN_EXPIRE_DEFAULT
        if not (self._TOKEN_EXPIRE_MIN <= value <= self._TOKEN_EXPIRE_MAX):
            _logger.warning(
                "admin.token_expire_hours 超出范围 (%d)，有效范围 %d-%d，使用默认值 %d",
                value, self._TOKEN_EXPIRE_MIN, self._TOKEN_EXPIRE_MAX, self._TOKEN_EXPIRE_DEFAULT,
            )
            return self._TOKEN_EXPIRE_DEFAULT
        return value


class Settings:
    """全局配置，从 config.yaml 加载，不存在时使用默认值。"""

    def __init__(self):
        if CONFIG_PATH.exists():
            with open(CONFIG_PATH, "r", encoding="utf-8") as f:
                file_config = yaml.safe_load(f) or {}
            # 深度合并默认值和文件配置
            self._config = self._deep_merge(DEFAULT_CONFIG, file_config)
        else:
            self._config = DEFAULT_CONFIG.copy()
            _logger.warning("=" * 70)
            _logger.warning("config.yaml not found — using INSECURE defaults!")
            _logger.warning("  • admin.password is 'changeme' — anyone can log in.")
            _logger.warning("  • admin.jwt_secret is 'change-me-in-production' —")
            _logger.warning("    anyone can forge authentication tokens.")
            _logger.warning("  • llm.api_key is a placeholder — LLM calls will fail.")
            _logger.warning("Create config.yaml with real values before deploying.")
            _logger.warning("=" * 70)

    @staticmethod
    def _deep_merge(base: dict, override: dict) -> dict:
        result = base.copy()
        for key, value in override.items():
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                result[key] = Settings._deep_merge(result[key], value)
            else:
                result[key] = value
        return result

    def get(self, key, default=None):
        """按顶层 key 获取配置段。"""
        return self._config.get(key, default)

    @property
    def admin(self) -> AdminSettings:
        """管理后台配置段，支持属性访问和自动验证。"""
        return AdminSettings(self._config.get("admin", {}))

    @property
    def config(self):
        return self._config


settings = Settings()
