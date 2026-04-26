"""LLM chain manager: in-memory singleton tracking runtime chain state and handling auto-switching."""

import logging
import time
import threading

from sqlalchemy.orm import Session

from app.models.llm_config import LLMConfig
from app.models.model_fallback_setting import ModelFallbackSetting

_logger = logging.getLogger(__name__)


class _ChainState:
    """Runtime state for a single chain."""

    def __init__(self, current_config_id: int, group_id: str):
        self.current_config_id = current_config_id
        self.group_id = group_id
        self.failure_count = 0
        self.timeout_count = 0
        self.cooling_until = 0.0  # timestamp


class LLMChainManager:
    """Singleton that tracks chain states and handles auto-switching.

    Thread-safety: a single ``threading.Lock`` protects ``_states`` dict reads/writes.
    DB queries happen *outside* the lock to avoid holding it during I/O.
    """

    def __init__(self):
        self._states: dict[str, _ChainState] = {}  # group_id -> _ChainState
        self._lock = threading.Lock()

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def get_active_config(self, db: Session, group_id: str) -> LLMConfig | None:
        """Get the currently serving config for a chain.

        Handles cooldown recovery: when a cooling period expires we reset
        to the primary and return it.
        """
        with self._lock:
            state = self._states.get(group_id)

        if state is None:
            # First access - use the primary (role=primary)
            primary = db.query(LLMConfig).filter(
                LLMConfig.fallback_group_id == group_id,
                LLMConfig.role == "primary",
            ).first()
            if not primary:
                return None
            with self._lock:
                self._states[group_id] = _ChainState(primary.id, group_id)
            return primary

        # Check if a cooling model has recovered
        now = time.time()
        if state.cooling_until > 0 and now >= state.cooling_until:
            # Cooldown expired - reset to primary and try again
            primary = db.query(LLMConfig).filter(
                LLMConfig.fallback_group_id == group_id,
                LLMConfig.role == "primary",
            ).first()
            if primary:
                with self._lock:
                    state.current_config_id = primary.id
                    state.failure_count = 0
                    state.timeout_count = 0
                    state.cooling_until = 0.0
                return primary

        config = db.query(LLMConfig).filter(LLMConfig.id == state.current_config_id).first()
        return config

    def record_success(self, group_id: str):
        """Reset failure counters on success."""
        with self._lock:
            state = self._states.get(group_id)
            if state:
                state.failure_count = 0
                state.timeout_count = 0

    def record_failure(self, db: Session, group_id: str, is_timeout: bool = False):
        """Record a failure.  If threshold exceeded, switch to next fallback."""
        setting = (
            db.query(ModelFallbackSetting)
            .join(LLMConfig, ModelFallbackSetting.primary_llm_config_id == LLMConfig.id)
            .filter(LLMConfig.fallback_group_id == group_id)
            .first()
        )

        if not setting:
            return

        with self._lock:
            state = self._states.get(group_id)
            if not state:
                return

            if is_timeout:
                state.timeout_count += 1
            state.failure_count += 1
            # Snapshot values so we can release the lock before DB work
            fc = state.failure_count
            tc = state.timeout_count

        # Check thresholds (outside lock to avoid holding it during DB ops)
        should_switch = fc >= setting.failure_threshold or tc >= setting.timeout_threshold

        if should_switch:
            self._switch_to_next(db, group_id, setting)

    def reset_chain(self, group_id: str):
        """Remove chain from tracking (e.g., when chain is dissolved)."""
        with self._lock:
            self._states.pop(group_id, None)

    def get_chain_status(self, group_id: str) -> dict:
        """Return current runtime status for API consumption."""
        with self._lock:
            state = self._states.get(group_id)

        if not state:
            return {
                "active_config_id": None,
                "failure_count": 0,
                "timeout_count": 0,
                "status": "normal",
                "next_available_at": None,
            }

        now = time.time()
        if state.cooling_until > now:
            status = "cooling"
            next_available = state.cooling_until
        elif state.failure_count > 0:
            status = "degraded"
            next_available = None
        else:
            status = "normal"
            next_available = None

        return {
            "active_config_id": state.current_config_id,
            "failure_count": state.failure_count,
            "timeout_count": state.timeout_count,
            "status": status,
            "next_available_at": next_available,
        }

    # ------------------------------------------------------------------
    # Internal
    # ------------------------------------------------------------------

    def _switch_to_next(self, db: Session, group_id: str, setting: ModelFallbackSetting):
        """Switch to the next fallback in the chain."""
        with self._lock:
            state = self._states.get(group_id)
            if not state:
                return
            old_config_id = state.current_config_id

        # Find all configs in chain ordered by fallback_order
        all_configs = (
            db.query(LLMConfig)
            .filter(LLMConfig.fallback_group_id == group_id)
            .order_by(LLMConfig.fallback_order)
            .all()
        )

        # Find current position
        current_idx = None
        for i, cfg in enumerate(all_configs):
            if cfg.id == old_config_id:
                current_idx = i
                break

        if current_idx is None:
            return

        # Try next config
        next_idx = current_idx + 1
        if next_idx >= len(all_configs):
            # All models exhausted - set cooling on current, will try primary after cooldown
            with self._lock:
                state.cooling_until = time.time() + setting.cooldown_seconds
                state.failure_count = 0
                state.timeout_count = 0
            _logger.warning(
                "Chain %s: all models exhausted, entering cooldown for %ds",
                group_id,
                setting.cooldown_seconds,
            )
            return

        next_config = all_configs[next_idx]

        # Update DB active status
        old_config = db.query(LLMConfig).filter(LLMConfig.id == old_config_id).first()
        if old_config:
            old_config.is_active = False
        next_config.is_active = True
        db.commit()

        _logger.info(
            "Chain %s: switched from config %d to config %d (fallback order %d)",
            group_id,
            old_config_id,
            next_config.id,
            next_config.fallback_order,
        )

        with self._lock:
            state.current_config_id = next_config.id
            state.failure_count = 0
            state.timeout_count = 0


# Module-level singleton
_chain_manager = LLMChainManager()


def get_chain_manager() -> LLMChainManager:
    """Return the global LLMChainManager singleton."""
    return _chain_manager
