import yaml
from pathlib import Path

# 项目根目录：backend/ 的上一级
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
CONFIG_PATH = PROJECT_ROOT / "config.yaml"

DEFAULT_CONFIG = {
    "server": {
        "host": "0.0.0.0",
        "port": 8000,
        "cors_origins": ["http://localhost:5173"],
    },
    "database": {
        "url": "sqlite:///./data/app.db",
    },
    "admin": {
        "username": "admin",
        "password": "changeme",
        "jwt_secret": "change-me-in-production",
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
    "frontend": {
        "title": "用友产业案例教学项目课程定制系统",
    },
}


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
            print("=" * 70)
            print("⚠️  WARNING: config.yaml not found — using INSECURE defaults!  ⚠️")
            print("  • admin.password is 'changeme' — anyone can log in.")
            print("  • admin.jwt_secret is 'change-me-in-production' —")
            print("    anyone can forge authentication tokens.")
            print("  • llm.api_key is a placeholder — LLM calls will fail.")
            print("Create config.yaml with real values before deploying.")
            print("=" * 70)

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
    def config(self):
        return self._config


settings = Settings()
