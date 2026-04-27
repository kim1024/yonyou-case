"""LLM chain manager: DB-backed singleton tracking runtime chain state and handling auto-switching."""

import logging
import time

from sqlalchemy.orm import Session

from app.models.llm_config import LLMConfig
from app.models.model_fallback_setting import ModelFallbackSetting
from app.models.chain_runtime_state import ChainRuntimeState

_logger = logging.getLogger(__name__)


class LLMChainManager:
    """Singleton that tracks chain states and handles auto-switching.

    State is persisted in the ``chain_runtime_states`` table so it is shared
    across all workers / processes.  A few ms of DB overhead per call is
    negligible because each LLM invocation takes 1-60 seconds.
    """

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def get_active_config(self, db: Session, group_id: str) -> LLMConfig | None:
        """Get the currently serving config for a chain.

        Handles cooldown recovery: when a cooling period expires we reset
        to the primary and return it.
        """
        state = db.query(ChainRuntimeState).filter(
            ChainRuntimeState.group_id == group_id
        ).first()

        if state is None:
            return self._initialize_enabled_chain(db, group_id)

        now = time.time()
        if state.cooling_until > 0:
            if now < state.cooling_until:
                return None
            primary = self._restore_primary(db, group_id, state)
            if primary:
                return primary

        if state.current_config_id is None:
            return self._get_current_chain_config(db, group_id)

        config = db.query(LLMConfig).filter(LLMConfig.id == state.current_config_id).first()
        if config:
            return config
        return self._get_current_chain_config(db, group_id)

    def record_success(self, db: Session, group_id: str):
        """Reset failure counters on success."""
        state = db.query(ChainRuntimeState).filter(
            ChainRuntimeState.group_id == group_id
        ).first()
        if state:
            state.failure_count = 0
            state.timeout_count = 0
            db.commit()

    def record_failure(self, db: Session, group_id: str, is_timeout: bool = False) -> str:
        """Record a failure and decide the next chain action.

        The chain advances only after reaching the configured consecutive
        failure threshold. If the chain is exhausted, we enter cooldown before
        trying the primary again.
        """
        setting = (
            db.query(ModelFallbackSetting)
            .join(LLMConfig, ModelFallbackSetting.primary_llm_config_id == LLMConfig.id)
            .filter(LLMConfig.fallback_group_id == group_id)
            .first()
        )

        if not setting:
            return "unavailable"

        # Use FOR UPDATE to safely read-modify-write the state row.
        state = db.query(ChainRuntimeState).filter(
            ChainRuntimeState.group_id == group_id
        ).with_for_update().first()

        if not state:
            current = self._initialize_enabled_chain(db, group_id)
            if not current:
                return "unavailable"
            state = db.query(ChainRuntimeState).filter(
                ChainRuntimeState.group_id == group_id
            ).with_for_update().first()
            if not state:
                return "unavailable"

        if is_timeout:
            state.timeout_count += 1
        state.failure_count += 1
        should_switch = state.failure_count >= setting.failure_threshold
        db.commit()

        if not should_switch:
            return "retry"

        return "switched" if self._switch_to_next(db, group_id, setting) else "cooldown"

    def reset_chain(self, db: Session, group_id: str):
        """Remove chain from tracking (e.g., when chain is dissolved)."""
        state = db.query(ChainRuntimeState).filter(
            ChainRuntimeState.group_id == group_id
        ).first()
        if state:
            db.delete(state)
            db.commit()

    def get_chain_status(self, db: Session, group_id: str) -> dict:
        """Return current runtime status for API consumption."""
        enabled_config = self._get_enabled_chain_config(db, group_id)
        primary = self._get_primary_config(db, group_id)

        state = db.query(ChainRuntimeState).filter(
            ChainRuntimeState.group_id == group_id
        ).first()

        if not enabled_config:
            return {
                "active_config_id": None,
                "failure_count": 0,
                "timeout_count": 0,
                "status": "idle",
                "next_available_at": None,
                "is_enabled": False,
            }

        now = time.time()
        if state is None:
            current = self._initialize_enabled_chain(db, group_id) or primary or enabled_config
            return {
                "active_config_id": current.id if current else None,
                "failure_count": 0,
                "timeout_count": 0,
                "status": "normal",
                "next_available_at": None,
                "is_enabled": True,
            }

        if state.cooling_until > 0 and now >= state.cooling_until:
            current = self._restore_primary(db, group_id, state) or primary or enabled_config
            return {
                "active_config_id": current.id if current else None,
                "failure_count": 0,
                "timeout_count": 0,
                "status": "normal",
                "next_available_at": None,
                "is_enabled": True,
            }

        if state.cooling_until > now:
            status = "cooling"
            next_available = state.cooling_until
            active_config_id = None
        else:
            active_config_id = state.current_config_id or (primary.id if primary else enabled_config.id)
            current = db.query(LLMConfig).filter(LLMConfig.id == active_config_id).first() if active_config_id else None
            if current and enabled_config.id != current.id:
                self._set_chain_active_config(db, group_id, current.id)
                db.commit()

            if primary and active_config_id and active_config_id != primary.id:
                status = "degraded"
            elif state.failure_count > 0 or state.timeout_count > 0:
                status = "degraded"
            else:
                status = "normal"
            next_available = None

        return {
            "active_config_id": active_config_id,
            "failure_count": state.failure_count,
            "timeout_count": state.timeout_count,
            "status": status,
            "next_available_at": next_available,
            "is_enabled": True,
        }

    def has_state(self, db: Session, group_id: str) -> bool:
        return db.query(ChainRuntimeState).filter(
            ChainRuntimeState.group_id == group_id
        ).first() is not None

    # ------------------------------------------------------------------
    # Internal
    # ------------------------------------------------------------------

    def _initialize_enabled_chain(self, db: Session, group_id: str) -> LLMConfig | None:
        enabled_config = self._get_enabled_chain_config(db, group_id)
        if not enabled_config:
            return None

        primary = self._get_primary_config(db, group_id)
        target = primary or enabled_config

        if enabled_config.id != target.id:
            self._set_chain_active_config(db, group_id, target.id)

        state = ChainRuntimeState(
            group_id=group_id,
            current_config_id=target.id,
        )
        db.merge(state)
        db.commit()

        return target

    def _get_enabled_chain_config(self, db: Session, group_id: str) -> LLMConfig | None:
        return (
            db.query(LLMConfig)
            .filter(
                LLMConfig.fallback_group_id == group_id,
                LLMConfig.is_active == True,  # noqa: E712
            )
            .order_by(LLMConfig.fallback_order, LLMConfig.id)
            .first()
        )

    # ------------------------------------------------------------------
    # Internal
    # ------------------------------------------------------------------

    def _switch_to_next(self, db: Session, group_id: str, setting: ModelFallbackSetting) -> bool:
        """Switch to the next fallback in the chain."""
        state = db.query(ChainRuntimeState).filter(
            ChainRuntimeState.group_id == group_id
        ).with_for_update().first()
        if not state:
            return False
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
            return False

        # Try next config
        next_idx = current_idx + 1
        if next_idx >= len(all_configs):
            self._enter_cooldown(db, group_id, setting.cooldown_seconds, state=state)
            _logger.warning(
                "Chain %s: all models exhausted, entering cooldown for %ds",
                group_id,
                setting.cooldown_seconds,
            )
            return False

        next_config = all_configs[next_idx]
        self._set_chain_active_config(db, group_id, next_config.id)

        _logger.info(
            "Chain %s: switched from config %d to config %d (fallback order %d)",
            group_id,
            old_config_id,
            next_config.id,
            next_config.fallback_order,
        )

        state.current_config_id = next_config.id
        state.failure_count = 0
        state.timeout_count = 0
        state.cooling_until = 0.0
        db.commit()
        return True

    def _get_primary_config(self, db: Session, group_id: str) -> LLMConfig | None:
        return (
            db.query(LLMConfig)
            .filter(
                LLMConfig.fallback_group_id == group_id,
                LLMConfig.role == "primary",
            )
            .first()
        )

    def _get_current_chain_config(self, db: Session, group_id: str) -> LLMConfig | None:
        current = (
            db.query(LLMConfig)
            .filter(
                LLMConfig.fallback_group_id == group_id,
                LLMConfig.is_active == True,  # noqa: E712
            )
            .order_by(LLMConfig.fallback_order, LLMConfig.id)
            .first()
        )
        if current:
            return current
        return self._get_primary_config(db, group_id)

    def _set_chain_active_config(self, db: Session, group_id: str, active_config_id: int | None):
        configs = db.query(LLMConfig).filter(LLMConfig.fallback_group_id == group_id).all()
        for cfg in configs:
            cfg.is_active = cfg.id == active_config_id
        # Caller is responsible for committing.

    def _restore_primary(self, db: Session, group_id: str, state: ChainRuntimeState) -> LLMConfig | None:
        primary = self._get_primary_config(db, group_id)
        if not primary:
            return None
        self._set_chain_active_config(db, group_id, primary.id)
        state.current_config_id = primary.id
        state.failure_count = 0
        state.timeout_count = 0
        state.cooling_until = 0.0
        db.commit()
        return primary

    def _enter_cooldown(self, db: Session, group_id: str, cooldown_seconds: int, state: ChainRuntimeState | None = None):
        if state is None:
            state = db.query(ChainRuntimeState).filter(
                ChainRuntimeState.group_id == group_id
            ).with_for_update().first()
        if not state:
            return
        state.cooling_until = time.time() + cooldown_seconds
        state.failure_count = 0
        state.timeout_count = 0
        db.commit()


# Module-level singleton
_chain_manager = LLMChainManager()


def get_chain_manager() -> LLMChainManager:
    """Return the global LLMChainManager singleton."""
    return _chain_manager
