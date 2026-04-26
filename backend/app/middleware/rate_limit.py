"""速率限制中间件及配置。"""
import asyncio
import logging
import time
import threading

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse

_logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# 1. RateLimitConfig — 单例内存缓存
# ---------------------------------------------------------------------------

class RateLimitConfig:
    """从 DB 加载并缓存速率限制参数，支持运行时热更新。"""

    DEFAULTS = {
        "generate_max_requests": 10,
        "generate_window_seconds": 3600,
        "generate_cooldown_seconds": 30,
        "max_concurrent": 3,
    }

    def __init__(self):
        self._settings: dict = dict(self.DEFAULTS)

    # ---- DB 初始化 ----
    def load_from_db(self, db):
        """读取 security_settings 表，缺失的 key 自动插入默认值。"""
        from app.models.security_setting import SecuritySetting

        for key, default_val in self.DEFAULTS.items():
            row = db.query(SecuritySetting).filter(SecuritySetting.key == key).first()
            if row is None:
                db.add(SecuritySetting(
                    key=key,
                    value=str(default_val),
                    description=key,
                ))
                self._settings[key] = default_val
            else:
                try:
                    self._settings[key] = int(row.value)
                except (ValueError, TypeError):
                    self._settings[key] = default_val
        db.commit()

    # ---- 运行时热更新 ----
    def update(self, settings_dict: dict):
        """将 {key: value} 合并到内存缓存。"""
        for k, v in settings_dict.items():
            if k in self.DEFAULTS:
                self._settings[k] = int(v)

    # ---- 读取 ----
    def get(self, key, default=None):
        return self._settings.get(key, default)


# 模块级单例
rate_limit_config = RateLimitConfig()


# ---------------------------------------------------------------------------
# 2. SlidingWindowRateLimiter — 基于 IP 的滑动窗口
# ---------------------------------------------------------------------------

class SlidingWindowRateLimiter:
    """线程安全的滑动窗口限流器（按 IP 记录请求时间戳）。"""

    def __init__(self):
        self._records: dict[str, list[float]] = {}
        self._lock = threading.Lock()
        self._last_cleanup: float = time.monotonic()

    def is_rate_limited(
        self, key: str, max_requests: int, window_seconds: int
    ) -> tuple[bool, int]:
        """
        检查 key 是否被限流。

        返回 (limited, retry_after_seconds)。
        limited=True 时 retry_after > 0。
        """
        now = time.time()
        cutoff = now - window_seconds

        with self._lock:
            self._maybe_cleanup(now)

            timestamps = self._records.get(key, [])
            # 裁剪过期记录
            timestamps = [t for t in timestamps if t > cutoff]

            if len(timestamps) >= max_requests:
                oldest = timestamps[0]
                retry_after = int(window_seconds - (now - oldest)) + 1
                retry_after = max(retry_after, 1)
                return True, retry_after

            timestamps.append(now)
            self._records[key] = timestamps
            return False, 0

    # ---- 内部辅助 ----
    def _maybe_cleanup(self, now: float):
        """每 60 秒清理一次空/过期条目。"""
        if now - self._last_cleanup < 60:
            return
        self._last_cleanup = now
        # 使用配置的窗口时长（确保动态更新生效）
        window = rate_limit_config.get("generate_window_seconds", 3600)
        cutoff = now - window
        empty_keys = [
            k for k, ts in self._records.items()
            if not ts or ts[-1] <= cutoff
        ]
        for k in empty_keys:
            del self._records[k]


# ---------------------------------------------------------------------------
# 3. ConcurrentRequestLimiter — 全局并发控制
# ---------------------------------------------------------------------------

class ConcurrentRequestLimiter:
    """异步全局并发请求限制器（基于 asyncio.Lock 计数）。"""

    def __init__(self, max_concurrent: int = 3):
        self._max = max_concurrent
        self._active = 0
        self._lock = asyncio.Lock()

    async def try_acquire(self) -> bool:
        async with self._lock:
            if self._active >= self._max:
                return False
            self._active += 1
            return True

    async def release(self):
        async with self._lock:
            self._active = max(0, self._active - 1)


# ---------------------------------------------------------------------------
# 4. RateLimitMiddleware — Starlette 中间件
# ---------------------------------------------------------------------------

class RateLimitMiddleware(BaseHTTPMiddleware):
    """拦截 POST /api/generate，依次执行滑动窗口 → 冷却 → 并发检查。"""

    TARGET_PATH = "/api/generate"

    def __init__(self, app):
        super().__init__(app)
        self._limiter = SlidingWindowRateLimiter()
        self._concurrent = ConcurrentRequestLimiter(
            max_concurrent=rate_limit_config.get("max_concurrent", 3)
        )
        # 记录每个 IP 上次成功请求的时间，用于冷却检查
        self._last_request: dict[str, float] = {}
        self._cooldown_lock = threading.Lock()
        self._last_cooldown_cleanup: float = time.monotonic()

    # ---- IP 提取 ----
    @staticmethod
    def _get_client_ip(request: Request) -> str:
        forwarded = request.headers.get("x-forwarded-for", "").split(",")[0].strip()
        if forwarded:
            return forwarded
        real_ip = request.headers.get("x-real-ip", "")
        if real_ip:
            return real_ip
        return request.client.host if request.client else "unknown"

    # ---- 主调度 ----
    async def dispatch(self, request: Request, call_next):
        # 仅拦截 POST /api/generate
        if request.method != "POST" or request.url.path != self.TARGET_PATH:
            return await call_next(request)

        client_ip = self._get_client_ip(request)
        max_requests = rate_limit_config.get("generate_max_requests", 10)
        window = rate_limit_config.get("generate_window_seconds", 3600)
        cooldown = rate_limit_config.get("generate_cooldown_seconds", 30)

        # 动态更新并发限制
        new_max = rate_limit_config.get("max_concurrent", 3)
        if new_max != self._concurrent._max:
            self._concurrent._max = new_max

        # --- Stage 1: 滑动窗口限流 ---
        limited, retry_after = self._limiter.is_rate_limited(
            client_ip, max_requests, window
        )
        if limited:
            _logger.warning(
                "Rate limited IP=%s path=%s retry_after=%d",
                client_ip, self.TARGET_PATH, retry_after,
            )
            return JSONResponse(
                status_code=429,
                content={
                    "detail": "Too many requests",
                    "message": f"请求过于频繁，请在 {retry_after} 秒后重试",
                    "retry_after": retry_after,
                },
                headers={"Retry-After": str(retry_after)},
            )

        # --- Stage 2: 冷却间隔检查 ---
        now = time.time()
        with self._cooldown_lock:
            last_ts = self._last_request.get(client_ip, 0)
            elapsed = now - last_ts
            if elapsed < cooldown:
                cd_remaining = int(cooldown - elapsed) + 1
                cd_remaining = max(cd_remaining, 1)
                _logger.warning(
                    "Cooldown IP=%s path=%s remaining=%d",
                    client_ip, self.TARGET_PATH, cd_remaining,
                )
                return JSONResponse(
                    status_code=429,
                    content={
                        "detail": "Cooldown period active",
                        "message": f"请求冷却中，请在 {cd_remaining} 秒后重试",
                        "retry_after": cd_remaining,
                    },
                    headers={"Retry-After": str(cd_remaining)},
                )

            # 定期清理过期的冷却记录（每 60 秒）
            monotonic_now = time.monotonic()
            if monotonic_now - self._last_cooldown_cleanup > 60:
                self._last_cooldown_cleanup = monotonic_now
                cutoff = now - cooldown * 2
                expired_ips = [ip for ip, ts in self._last_request.items() if ts < cutoff]
                for ip in expired_ips:
                    del self._last_request[ip]

        # --- Stage 3: 并发检查 ---
        acquired = await self._concurrent.try_acquire()
        if not acquired:
            _logger.warning(
                "Concurrency limit hit IP=%s path=%s",
                client_ip, self.TARGET_PATH,
            )
            retry_concurrent = cooldown  # 给出一个合理的重试时间
            return JSONResponse(
                status_code=503,
                content={
                    "detail": "Service temporarily unavailable",
                    "message": "当前并发请求已满，请稍后重试",
                    "retry_after": retry_concurrent,
                },
                headers={"Retry-After": str(retry_concurrent)},
            )

        # --- 执行请求 ---
        try:
            response = await call_next(request)
            # 记录成功请求时间（用于冷却检查）
            with self._cooldown_lock:
                self._last_request[client_ip] = time.time()
            return response
        finally:
            await self._concurrent.release()
