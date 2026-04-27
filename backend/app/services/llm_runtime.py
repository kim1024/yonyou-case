"""Helpers for resolving and enforcing the active LLM runtime target."""

from sqlalchemy import case
from sqlalchemy.orm import Session

from app.models.llm_config import LLMConfig


def deactivate_all_configs(db: Session, exclude_config_id: int | None = None) -> None:
    """Deactivate every active LLM config, optionally keeping one config active."""
    query = db.query(LLMConfig).filter(LLMConfig.is_active == True)  # noqa: E712
    if exclude_config_id is not None:
        query = query.filter(LLMConfig.id != exclude_config_id)
    query.update({"is_active": False}, synchronize_session=False)


def get_enabled_chain_member(db: Session) -> LLMConfig | None:
    """Return the active config inside an enabled chain, if any."""
    return (
        db.query(LLMConfig)
        .filter(
            LLMConfig.is_active == True,  # noqa: E712
            LLMConfig.fallback_group_id.isnot(None),
        )
        .order_by(
            case((LLMConfig.role == "primary", 0), else_=1),
            LLMConfig.fallback_order,
            LLMConfig.id,
        )
        .first()
    )


def get_active_standalone_config(db: Session) -> LLMConfig | None:
    """Return the active standalone config, if any."""
    return (
        db.query(LLMConfig)
        .filter(
            LLMConfig.is_active == True,  # noqa: E712
            LLMConfig.fallback_group_id.is_(None),
        )
        .order_by(LLMConfig.id)
        .first()
    )


def resolve_runtime_config(db: Session) -> LLMConfig | None:
    """Resolve the config that should actually serve requests.

    Chain members take precedence over standalone configs so historical
    dirty data does not break the runtime routing rules.
    """
    enabled_chain_member = get_enabled_chain_member(db)
    if enabled_chain_member and enabled_chain_member.fallback_group_id:
        from app.services.llm_chain_manager import get_chain_manager

        runtime_config = get_chain_manager().get_active_config(db, enabled_chain_member.fallback_group_id)
        if runtime_config:
            return runtime_config

    return get_active_standalone_config(db)


def normalize_runtime_state(db: Session) -> LLMConfig | None:
    """Collapse dirty multi-active states down to one winner.

    Preference order:
    1. An active chain member
    2. An active standalone config
    3. Otherwise no active config
    """
    winner = None
    enabled_chain_member = get_enabled_chain_member(db)
    if enabled_chain_member and enabled_chain_member.fallback_group_id:
        from app.services.llm_chain_manager import get_chain_manager

        chain_status = get_chain_manager().get_chain_status(db, enabled_chain_member.fallback_group_id)
        active_config_id = chain_status.get("active_config_id")
        if active_config_id is not None:
            winner = db.query(LLMConfig).filter(LLMConfig.id == active_config_id).first()
        else:
            # 冷却期仍保留当前链路的启用标记，避免管理端把链路误判为已失效。
            winner = get_enabled_chain_member(db)

    if not winner:
        winner = get_active_standalone_config(db)

    active_count = db.query(LLMConfig).filter(LLMConfig.is_active == True).count()  # noqa: E712

    if not winner:
        if active_count > 0:
            deactivate_all_configs(db)
            db.commit()
        return None

    if active_count > 1 or not winner.is_active:
        deactivate_all_configs(db, exclude_config_id=winner.id)
        winner.is_active = True
        db.commit()
        db.refresh(winner)

    return winner
