"""Background task service for async plan generation.

The POST /api/generate endpoint creates a pending GeneratedPlan and enqueues
``run_generation_background`` via FastAPI BackgroundTasks.  This module owns
the full LLM call + template-fallback lifecycle.
"""

import json
import logging
from datetime import datetime, timezone

import httpx
from sqlalchemy.orm import Session

from app.config import settings
from app.database import SessionLocal
from app.models.enterprise import Enterprise
from app.models.generated_plan import GeneratedPlan
from app.models.llm_config import LLMConfig
from app.models.major import Hour
from app.models.model_fallback_setting import ModelFallbackSetting
from app.models.prompt_template import PromptTemplate
from app.models.prompt_version import PromptVersion
from app.models.token_usage_log import TokenUsageLog
from app.services.generation_utils import (
    DELIVERABLES,
    _build_fallback_json,
    _normalize_title_subtitle,
    _parse_llm_json,
    _safe,
)
from app.services.llm_chain_manager import get_chain_manager
from app.services.llm_runtime import normalize_runtime_state, resolve_runtime_config
from app.services.token_quota_service import enforce_quota

_logger = logging.getLogger(__name__)

# Maximum value max_tokens is allowed to take — prevents mis-configured models
# from using the full context-window as generation limit.
_MAX_TOKENS_CAP = 16384


# ---------------------------------------------------------------------------
# Public entry point
# ---------------------------------------------------------------------------

def run_generation_background(plan_id: int) -> None:
    """Entry point for FastAPI ``BackgroundTasks``.

    Creates its own DB session (independent of the request lifecycle) and
    delegates to ``_run_generation``.  Any uncaught exception results in the
    plan being marked as *failed* with a sanitized error message.
    """
    db = SessionLocal()
    try:
        _run_generation(db, plan_id)
    except Exception as exc:
        _logger.error("Generation failed for plan %d: %s", plan_id, exc, exc_info=True)
        try:
            _mark_failed(db, plan_id, _sanitize_error(exc))
        except Exception:
            _logger.error("Failed to mark plan %d as failed", plan_id, exc_info=True)
    finally:
        db.close()


# ---------------------------------------------------------------------------
# Core generation logic
# ---------------------------------------------------------------------------
def _run_generation(db: Session, plan_id: int) -> None:
    """Full generation lifecycle — mutates the existing plan record."""

    # 1. Read & validate plan
    plan = db.query(GeneratedPlan).filter(GeneratedPlan.id == plan_id).first()
    if not plan:
        _logger.error("Plan %d not found", plan_id)
        return
    if plan.status != "pending":
        _logger.warning("Plan %d status is %s, skipping", plan_id, plan.status)
        return

    # 2. Mark processing
    plan.status = "processing"
    plan.started_at = datetime.now(timezone.utc)
    db.commit()

    # 3. Extract enterprise info from the plan record
    major = plan.major or ""
    industry = plan.industry or ""
    enterprise_name = plan.enterprise or ""
    region = plan.province or ""
    hour = plan.hour or 8

    enterprise = db.query(Enterprise).filter(
        Enterprise.customer_name == enterprise_name,
        Enterprise.industry == industry,
        Enterprise.province == region,
    ).first()
    company_intro = enterprise.company_intro if enterprise else "暂无企业简介"
    yonyou_content = enterprise.yonyou_content if enterprise else "暂无建设内容"

    # 4. LLM config resolution — mirror wizard.py lines 366-387
    llm_config_id = None
    try:
        db_llm = normalize_runtime_state(db) or resolve_runtime_config(db)
    except Exception:
        db_llm = None

    if db_llm:
        api_key = db_llm.api_key
        api_base_url = db_llm.api_base_url
        model = db_llm.model
        temperature = db_llm.temperature or 0.7
        max_tokens = db_llm.max_tokens or 4000
        timeout = db_llm.timeout or 60
        llm_config_id = db_llm.id
    else:
        llm_cfg = settings.get("llm", {})
        api_key = llm_cfg.get("api_key", "")
        api_base_url = llm_cfg.get("api_base_url", "https://api.openai.com/v1")
        model = llm_cfg.get("model", "gpt-4o")
        temperature = llm_cfg.get("temperature", 0.7)
        max_tokens = llm_cfg.get("max_tokens", 4000)
        timeout = llm_cfg.get("timeout", 60)

    # 5. Fallback chain detection — mirror wizard.py lines 389-431
    chain_manager = get_chain_manager()
    use_chain = False
    chain_group_id = None
    chain_primary_config_id = None
    chain_timeout_seconds = None
    chain_failure_threshold = 1
    chain_in_cooling = False
    max_retries = 1

    if db_llm and db_llm.fallback_group_id:
        use_chain = True
        chain_group_id = db_llm.fallback_group_id
        chain_setting = (
            db.query(ModelFallbackSetting)
            .join(LLMConfig, ModelFallbackSetting.primary_llm_config_id == LLMConfig.id)
            .filter(LLMConfig.fallback_group_id == chain_group_id)
            .first()
        )
        if chain_setting:
            chain_timeout_seconds = chain_setting.timeout_seconds
            chain_primary_config_id = chain_setting.primary_llm_config_id
            chain_failure_threshold = max(1, chain_setting.failure_threshold or 1)
        chain_config = chain_manager.get_active_config(db, chain_group_id)
        if chain_config:
            active_config = chain_config
            api_key = active_config.api_key
            api_base_url = active_config.api_base_url
            model = active_config.model
            temperature = active_config.temperature or 0.7
            max_tokens = active_config.max_tokens or 4000
            timeout = max(chain_timeout_seconds or 0, active_config.timeout or 60)
            llm_config_id = active_config.id
            chain_size = db.query(LLMConfig).filter(
                LLMConfig.fallback_group_id == chain_group_id
            ).count()
            max_retries = max(1, chain_size * chain_failure_threshold)
        else:
            chain_in_cooling = True

    max_tokens = min(max_tokens, _MAX_TOKENS_CAP)

    # --- chain helpers (closures over mutable state) ---
    attempted_config_ids: set[int] = set()

    def _switch_chain_config(next_config):
        nonlocal api_key, api_base_url, model, temperature, max_tokens, timeout, llm_config_id
        api_key = next_config.api_key
        api_base_url = next_config.api_base_url
        model = next_config.model
        temperature = next_config.temperature or 0.7
        max_tokens = min(next_config.max_tokens or 4000, _MAX_TOKENS_CAP)
        timeout = chain_timeout_seconds or next_config.timeout or 60
        llm_config_id = next_config.id

    def _try_chain_failover(is_timeout: bool) -> bool:
        if not use_chain or not chain_group_id or llm_config_id is None:
            return False
        previous_config_id = llm_config_id
        action = chain_manager.record_failure(db, chain_group_id, is_timeout=is_timeout)
        if action == "retry":
            return True
        if action != "switched":
            return False
        next_config = chain_manager.get_active_config(db, chain_group_id)
        if (
            not next_config
            or next_config.id == previous_config_id
            or next_config.id in attempted_config_ids
        ):
            return False
        _switch_chain_config(next_config)
        # 链路共享限额，failover 后再次检查链路限额
        enforce_quota(db, llm_config_id)
        return True

    # 6. Pre-compute pricing & hour blocks
    hour_record = db.query(Hour).filter(
        Hour.value == hour,
        Hour.is_active == True,
    ).first()
    rate = hour_record.unit_price if hour_record and hour_record.unit_price else 2000
    total_cost = rate * hour

    hour_block1 = max(1, hour // 8)
    hour_block2 = max(1, hour // 8)
    hour_block3 = hour // 2
    hour_block4 = hour - hour_block1 - hour_block2 - hour_block3

    # 7. Prompt construction — mirror wizard.py lines 477-592
    db_prompt_content = None
    try:
        db_template = db.query(PromptTemplate).filter(
            PromptTemplate.scene == "课程方案生成",
            PromptTemplate.is_active == True,
        ).first()
        if db_template and db_template.current_version_id:
            db_version = db.query(PromptVersion).filter(
                PromptVersion.id == db_template.current_version_id
            ).first()
            if db_version:
                db_prompt_content = db_version.content
    except Exception:
        pass

    if db_prompt_content:
        try:
            prompt = db_prompt_content.format(
                major=_safe(major),
                industry=_safe(industry),
                enterprise_name=_safe(enterprise_name),
                region=_safe(region),
                hour=hour,
                total_cost=total_cost,
                company_intro=_safe(company_intro, 1000),
                yonyou_content=_safe(yonyou_content, 1000),
                hour_block1=hour_block1,
                hour_block2=hour_block2,
                hour_block3=hour_block3,
                hour_block4=hour_block4,
            )
        except KeyError as e:
            _logger.warning("提示词模板变量替换失败: %s，使用默认 prompt", e)
            db_prompt_content = None

    if not db_prompt_content:
        prompt = f"""请根据以下信息，生成一份产业案例教学课程设计方案。

专业方向：{_safe(major)}
行业：{_safe(industry)}
企业：{_safe(enterprise_name)}
地区：{_safe(region)}
课时：{hour}课时

<企业简介>
{_safe(company_intro, 1000)}
</企业简介>
<用友建设内容>
{_safe(yonyou_content, 1000)}
</用友建设内容>

请严格按照以下 JSON 结构输出（仅输出 JSON，不要输出其他内容）：

{{
  "title": "{_safe(enterprise_name)}案例",
  "subtitle": "教学课程方案",
  "introduction": "本教学案例基于<b class=\\"highlight\\">{_safe(enterprise_name)}</b>公司的真实业务场景，结合<b class=\\"highlight\\">{_safe(industry)}</b>专业技术，设计了一套完整的<b class=\\"highlight\\">{hour}</b>课时教学方案。通过本案例的学习，学员将深入理解<b class=\\"highlight\\">{_safe(industry)}</b>行业与<b class=\\"highlight\\">{_safe(major)}</b>技术的融合应用，掌握实际项目中的核心技能。",
  "modules": [
    {{
      "name": "模块一：行业背景与需求分析",
      "hours": {hour_block1},
      "items": ["{industry}行业现状与发展趋势", "{enterprise_name}业务模式与技术需求分析", "数字化转型痛点与机遇"]
    }},
    {{
      "name": "模块二：技术基础与工具介绍",
      "hours": {hour_block2},
      "items": ["{major}核心技术原理与架构", "用友产品体系与解决方案概览", "开发环境搭建与工具链配置"]
    }},
    {{
      "name": "模块三：案例实战与项目实施",
      "hours": {hour_block3},
      "items": ["{enterprise_name}真实业务场景解析", "基于用友平台的功能开发与集成", "项目方案设计、实施与优化"]
    }},
    {{
      "name": "模块四：总结与拓展",
      "hours": {hour_block4},
      "items": ["项目成果展示与答辩", "{industry}领域最佳实践总结", "职业发展路径与学习资源推荐"]
    }}
  ],
  "positions": [
    {{
      "title": "{major}工程师",
      "description": ["负责{industry}领域的数据/系统开发", "参与企业数字化转型项目", "熟练使用用友产品体系"]
    }},
    {{
      "title": "{industry}解决方案架构师",
      "description": ["设计行业数字化解决方案", "对接客户需求与技术实现"]
    }},
    {{
      "title": "项目实施顾问",
      "description": ["负责用友产品在企业的落地实施", "提供客户培训与技术支持"]
    }},
    {{
      "title": "业务分析师",
      "description": ["分析{industry}业务流程与需求", "设计数字化优化方案"]
    }},
    {{
      "title": "技术项目经理",
      "description": ["管理{industry}领域IT项目", "协调团队与客户资源"]
    }},
    {{
      "title": "数字化运营专员",
      "description": ["负责{industry}领域数字化运营与持续优化", "监控系统运行指标，推动业务流程改进"]
    }}
  ],
  "deliverables": {json.dumps(DELIVERABLES, ensure_ascii=False)},
  "notes": "以上内容由 AI 生成，请结合实际教学需求进行调整。"
}}

要求：
1. 请根据实际信息丰富 introduction 的内容，使其不少于 100 字。
2. modules 中每个模块的 items 不少于 3 条。
3. positions 中岗位和描述需结合 {industry} 领域与 {major} 专业。
4. 仅输出 JSON，不要输出其他内容。
5. introduction 中需要强调的动态内容（企业名、行业名、专业名、课时数等），请用 HTML 标签包裹：<b class="highlight">xxx</b>，使其加粗并使用特殊颜色显示。"""

    # 8. Second quota check before LLM call
    if llm_config_id is not None:
        enforce_quota(db, llm_config_id)

    # 9. LLM invocation loop — mirror wizard.py lines 598-696
    last_error = RuntimeError("降级链处于冷却期，暂不调用大模型") if chain_in_cooling else None
    for attempt in range(max_retries):
        if chain_in_cooling:
            break
        if llm_config_id is not None:
            attempted_config_ids.add(llm_config_id)
        try:
            if api_key and api_key != "sk-xxx":
                base = api_base_url.rstrip("/")
                if not base.endswith("/v1"):
                    base = f"{base}/v1"
                response = httpx.post(
                    f"{base}/chat/completions",
                    headers={
                        "Authorization": f"Bearer {api_key}",
                        "Content-Type": "application/json",
                    },
                    json={
                        "model": model,
                        "messages": [{"role": "user", "content": prompt}],
                        "temperature": temperature,
                        "max_tokens": max_tokens,
                    },
                    timeout=timeout,
                )
                if response.status_code == 200:
                    result = response.json()
                    content = result["choices"][0]["message"]["content"]

                    # Record token usage (chain mode: always log to primary config)
                    usage = result.get("usage", {})
                    quota_config_id = (
                        chain_primary_config_id
                        if use_chain and chain_primary_config_id
                        else llm_config_id
                    )
                    if quota_config_id:
                        log = TokenUsageLog(
                            llm_config_id=quota_config_id,
                            model=model,
                            prompt_tokens=usage.get("prompt_tokens", 0),
                            completion_tokens=usage.get("completion_tokens", 0),
                            total_tokens=usage.get("total_tokens", 0),
                        )
                        db.add(log)

                    # Parse LLM JSON
                    plan_json = _parse_llm_json(content)
                    if plan_json is not None:
                        _normalize_title_subtitle(plan_json, enterprise_name)
                        plan_json["deliverables"] = DELIVERABLES
                        plan_json["pricing"] = {
                            "hour": hour,
                            "unit_price": rate,
                            "total_cost": total_cost,
                        }
                        # UPDATE existing plan (not create new)
                        plan.plan_data = json.dumps(plan_json, ensure_ascii=False)
                        plan.plan_title = plan_json.get("title", "")
                        plan.source = "ai"
                        plan.status = "completed"
                        plan.error_message = None
                        try:
                            db.commit()
                        except Exception:
                            db.rollback()
                            raise
                        if use_chain:
                            chain_manager.record_success(db, chain_group_id)
                        _logger.info("Plan %d generated successfully (source=ai)", plan_id)
                        return
                    else:
                        _logger.warning("LLM 返回 JSON 解析失败，回退到模板")
                        last_error = ValueError("LLM 返回 JSON 解析失败")
                        if _try_chain_failover(is_timeout=False):
                            continue
                        break
                else:
                    _logger.warning(
                        "LLM API 返回非 200 状态码: %d, body_len=%d",
                        response.status_code,
                        len(response.text),
                    )
                    last_error = RuntimeError(f"LLM API status {response.status_code}")
                    if _try_chain_failover(is_timeout=False):
                        continue
                    break
        except httpx.TimeoutException as e:
            last_error = e
            _logger.warning(
                "LLM API call timeout (attempt %d/%d): %s",
                attempt + 1, max_retries, e,
            )
            if _try_chain_failover(is_timeout=True):
                continue
            break
        except Exception as e:
            last_error = e
            _logger.error(
                "AI API call failed (attempt %d/%d): %s",
                attempt + 1, max_retries, e,
            )
            if _try_chain_failover(is_timeout=False):
                continue
            break

    # 10. Template fallback — mirror wizard.py lines 698-724
    fallback = _build_fallback_json(
        enterprise_name, major, industry,
        hour, hour_block1, hour_block2,
        hour_block3, hour_block4,
        rate, total_cost,
    )
    plan.plan_data = json.dumps(fallback, ensure_ascii=False)
    plan.plan_title = fallback.get("title", "")
    plan.source = "template"
    plan.status = "completed"
    plan.error_message = (
        "大模型调用失败，已使用模板生成方案。请检查大模型配置（API Key、Base URL）是否正确。"
    )
    try:
        db.commit()
    except Exception:
        db.rollback()
        raise
    _logger.info("Plan %d generated with template fallback", plan_id)


# ---------------------------------------------------------------------------
# Error handling helpers
# ---------------------------------------------------------------------------

def _mark_failed(db: Session, plan_id: int, error_message: str) -> None:
    """Set plan status to 'failed' with a user-friendly error message."""
    plan = db.query(GeneratedPlan).filter(GeneratedPlan.id == plan_id).first()
    if not plan:
        return
    plan.status = "failed"
    plan.error_message = error_message
    try:
        db.commit()
    except Exception:
        db.rollback()
        raise


def _sanitize_error(e: Exception) -> str:
    """Map exceptions to user-friendly messages.  Original details go to logger only."""
    if isinstance(e, httpx.TimeoutException):
        return "大模型调用超时，请稍后重试"
    if isinstance(e, httpx.ConnectError):
        return "无法连接大模型服务"
    # HTTPException(429) from enforce_quota
    if hasattr(e, "status_code") and getattr(e, "status_code", None) == 429:
        detail = getattr(e, "detail", "")
        if isinstance(detail, dict) and detail.get("code") == "TOKEN_QUOTA_EXCEEDED":
            reset_at = detail.get("quota", {}).get("reset_at", "")
            if reset_at:
                return f"Token 配额已用尽（{reset_at} 重置），明日重置后可重新生成"
            return "Token 配额已用尽，明日重置后可重新生成"
        return "Token 配额已用尽，明日重置后可重新生成"
    if isinstance(e, (json.JSONDecodeError, ValueError)):
        return "大模型返回格式异常，已使用模板生成"
    return "生成失败，请稍后重试"
