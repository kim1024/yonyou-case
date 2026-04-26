import html
import json
import logging
import re
import uuid
from datetime import datetime, timedelta, timezone
from typing import Optional

import httpx
from fastapi import APIRouter, HTTPException, Depends, Query
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.config import settings
from app.database import get_db
from app.models.enterprise import Enterprise
from app.models.major import Major, Industry, MajorIndustry, Region, Hour
from app.models.llm_config import LLMConfig
from app.models.prompt_template import PromptTemplate
from app.models.prompt_version import PromptVersion
from app.models.token_usage_log import TokenUsageLog
from app.models.generated_plan import GeneratedPlan

DELIVERABLES = ["PPT", "视频", "指导书", "数据集", "代码包", "实操环境"]

_logger = logging.getLogger(__name__)

router = APIRouter(tags=["wizard"])


class GenerateStatusResponse(BaseModel):
    status: str  # "completed" | "pending" | "expired"
    data: Optional[dict] = None
    source: Optional[str] = None
    message: Optional[str] = None


@router.get("/api/majors")
def get_majors(db: Session = Depends(get_db)):
    """获取所有启用的专业列表（返回完整对象，支持卡片展示）"""
    majors = (
        db.query(Major)
        .filter(Major.is_active == True)
        .order_by(Major.sort_order, Major.id)
        .all()
    )
    return [
        {"id": m.id, "name": m.name, "description": m.description or "", "icon": m.icon or ""}
        for m in majors
    ]


@router.get("/api/industries")
def get_industries(
    major_id: int = Query(None),
    db: Session = Depends(get_db),
):
    """获取行业列表，可选按专业过滤"""
    if major_id is not None:
        # 按专业过滤：先查关联表，再取行业
        industry_ids = (
            db.query(MajorIndustry.industry_id)
            .filter(MajorIndustry.major_id == major_id)
            .subquery()
        )
        results = (
            db.query(Industry.name)
            .filter(Industry.is_active == True, Industry.id.in_(industry_ids))
            .order_by(Industry.sort_order, Industry.id)
            .all()
        )
    else:
        results = (
            db.query(Industry.name)
            .filter(Industry.is_active == True)
            .order_by(Industry.sort_order, Industry.id)
            .all()
        )
    return [r[0] for r in results]


@router.get("/api/config")
def get_config(db: Session = Depends(get_db)):
    first_hour = db.query(Hour).filter(Hour.is_active == True).order_by(Hour.value).first()
    rate = first_hour.unit_price if first_hour and first_hour.unit_price else 2000
    return {
        "title": settings.get("frontend", {}).get("title", "用友产业案例教学项目课程定制系统"),
        "rate_per_hour": rate,
    }


@router.post("/api/regions")
def get_regions(request: dict, db: Session = Depends(get_db)):
    """获取地区列表（支持按行业筛选，优先从 Region 表查询）"""
    industry = request.get("industry")
    if industry:
        # 1. 从 Region 表查询所有活跃地区名称
        region_rows = (
            db.query(Region.name)
            .filter(Region.is_active == True)
            .order_by(Region.sort_order, Region.id)
            .all()
        )
        region_names = [r[0] for r in region_rows]

        # 2. 从 Enterprise 表查询该行业下所有去重省份
        enterprise_provinces = [
            r[0] for r in (
                db.query(Enterprise.province)
                .filter(Enterprise.industry == industry)
                .distinct()
                .all()
            )
        ]

        if region_names:
            # 3. 取交集 — 只返回 Region 表中存在且 Enterprise 表中有对应企业记录的地区
            enterprise_set = set(enterprise_provinces)
            return [name for name in region_names if name in enterprise_set]

        # 4. 如果 Region 表为空，回退到仅从 Enterprise 表查询
        return enterprise_provinces

    # 5. 没有 industry 参数，返回所有活跃地区
    regions = (
        db.query(Region.name)
        .filter(Region.is_active == True)
        .order_by(Region.sort_order, Region.id)
        .all()
    )
    return [r[0] for r in regions]


@router.post("/api/enterprises")
def get_enterprises(request: dict, db: Session = Depends(get_db)):
    industry = request.get("industry")
    province = request.get("province")
    results = db.query(Enterprise.customer_name).filter(
        Enterprise.industry == industry,
        Enterprise.province == province
    ).all()
    return [r[0] for r in results]


@router.post("/api/enterprise-info")
def get_enterprise_info(request: dict, db: Session = Depends(get_db)):
    industry = request.get("industry")
    province = request.get("province")
    name = request.get("name")
    enterprise = db.query(Enterprise).filter(
        Enterprise.industry == industry,
        Enterprise.province == province,
        Enterprise.customer_name == name
    ).first()
    if not enterprise:
        raise HTTPException(status_code=404, detail="未找到企业")
    return {
        "customer_name": enterprise.customer_name,
        "province": enterprise.province,
        "city": enterprise.city,
        "industry": enterprise.industry,
        "company_intro": enterprise.company_intro or "",
        "yonyou_content": enterprise.yonyou_content or "",
    }


@router.get("/api/hours")
def get_hours(db: Session = Depends(get_db)):
    """获取所有启用的课时选项"""
    hours = (
        db.query(Hour)
        .filter(Hour.is_active == True)
        .order_by(Hour.sort_order, Hour.value)
        .all()
    )
    if hours:
        return [{"value": h.value, "label": h.label or f"{h.value}课时", "unit_price": h.unit_price or 2000} for h in hours]
    # 如果 Hour 表为空，返回默认值
    return [{"value": v, "label": f"{v}课时", "unit_price": 2000} for v in [8, 16, 24, 32]]


def _parse_llm_json(content: str) -> dict | None:
    """解析 LLM 返回的 JSON，失败则返回 None。"""
    try:
        # 如果包含 markdown 代码块标记，先提取 JSON 部分
        match = re.search(r'```(?:json)?\s*\n?(.*?)\n?```', content, re.DOTALL)
        if match:
            content = match.group(1).strip()

        parsed = json.loads(content)

        # 校验必填字段
        required_fields = ("title", "introduction", "modules", "positions", "deliverables")
        for field in required_fields:
            if field not in parsed:
                _logger.warning("LLM JSON 缺少必填字段: %s，回退模板", field)
                return None

        return parsed
    except (json.JSONDecodeError, TypeError) as e:
        _logger.warning("LLM 返回内容 JSON 解析失败: %s，回退模板", e)
        return None


def _normalize_title_subtitle(plan_json: dict, enterprise_name: str) -> None:
    """强制规范 title/subtitle 格式，不依赖 LLM 输出。

    目标格式：title = "{enterprise_name}案例"，subtitle = "教学课程方案"
    """
    plan_json["title"] = f"{enterprise_name}案例"
    plan_json["subtitle"] = "教学课程方案"


def _build_fallback_json(
    enterprise_name: str,
    major: str,
    industry: str,
    hour: int,
    hour_block1: int,
    hour_block2: int,
    hour_block3: int,
    hour_block4: int,
    rate: int,
    total_cost: int,
) -> dict:
    """构建兜底 JSON 模板。"""
    return {
        "title": f"{enterprise_name}案例",
        "subtitle": "教学课程方案",
        "introduction": (
            f'本教学案例基于<b class="highlight">{html.escape(enterprise_name)}</b>公司的真实业务场景，'
            f'结合<b class="highlight">{html.escape(industry)}</b>专业技术，'
            f'设计了一套完整的<b class="highlight">{hour}</b>课时教学方案。'
            f'通过本案例的学习，学员将深入理解'
            f'<b class="highlight">{html.escape(industry)}</b>行业与'
            f'<b class="highlight">{html.escape(major)}</b>技术的融合应用，'
            f'掌握实际项目中的核心技能。'
        ),
        "modules": [
            {
                "name": "模块一：行业背景与需求分析",
                "hours": hour_block1,
                "items": [
                    f"{industry}行业现状与发展趋势",
                    f"{enterprise_name}业务模式与技术需求分析",
                    "数字化转型痛点与机遇",
                ],
            },
            {
                "name": "模块二：技术基础与工具介绍",
                "hours": hour_block2,
                "items": [
                    f"{major}核心技术原理与架构",
                    "用友产品体系与解决方案概览",
                    "开发环境搭建与工具链配置",
                ],
            },
            {
                "name": "模块三：案例实战与项目实施",
                "hours": hour_block3,
                "items": [
                    f"{enterprise_name}真实业务场景解析",
                    "基于用友平台的功能开发与集成",
                    "项目方案设计、实施与优化",
                ],
            },
            {
                "name": "模块四：总结与拓展",
                "hours": hour_block4,
                "items": [
                    "项目成果展示与答辩",
                    f"{industry}领域最佳实践总结",
                    "职业发展路径与学习资源推荐",
                ],
            },
        ],
        "positions": [
            {
                "title": f"{major}工程师",
                "description": [
                    f"负责{industry}领域的数据/系统开发",
                    "参与企业数字化转型项目",
                    "熟练使用用友产品体系",
                ],
            },
            {
                "title": f"{industry}解决方案架构师",
                "description": [
                    "设计行业数字化解决方案",
                    "对接客户需求与技术实现",
                ],
            },
            {
                "title": "项目实施顾问",
                "description": [
                    "负责用友产品在企业的落地实施",
                    "提供客户培训与技术支持",
                ],
            },
            {
                "title": "业务分析师",
                "description": [
                    f"分析{industry}业务流程与需求",
                    "设计数字化优化方案",
                ],
            },
            {
                "title": "技术项目经理",
                "description": [
                    f"管理{industry}领域IT项目",
                    "协调团队与客户资源",
                ],
            },
            {
                "title": "数字化运营专员",
                "description": [
                    f"负责{industry}领域数字化运营与持续优化",
                    "监控系统运行指标，推动业务流程改进",
                ],
            },
        ],
        "deliverables": DELIVERABLES,
        "notes": "以上内容由 AI 生成，请结合实际教学需求进行调整。",
        "pricing": {
            "hour": hour,
            "unit_price": rate,
            "total_cost": total_cost,
        },
    }


@router.post("/api/generate")
def generate(request: dict, db: Session = Depends(get_db)):
    major = request.get("major", "")
    industry = request.get("industry", "")
    enterprise_name = request.get("enterprise", "")
    region = request.get("region", "")
    hour = request.get("hour", 8)

    # 读取并验证 client_request_id（可选，UUID 格式校验）
    client_request_id = request.get("client_request_id")
    if client_request_id:
        try:
            uuid.UUID(str(client_request_id))
        except (ValueError, TypeError):
            client_request_id = None

    # 查找企业信息
    enterprise = db.query(Enterprise).filter(
        Enterprise.customer_name == enterprise_name,
        Enterprise.industry == industry,
        Enterprise.province == region
    ).first()

    company_intro = enterprise.company_intro if enterprise else "暂无企业简介"
    yonyou_content = enterprise.yonyou_content if enterprise else "暂无建设内容"

    # 优先从数据库读取活跃配置
    llm_config_id = None
    try:
        db_llm = db.query(LLMConfig).filter(LLMConfig.is_active == True).first()
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
        # fallback 到 config.yaml
        llm_cfg = settings.get("llm", {})
        api_key = llm_cfg.get("api_key", "")
        api_base_url = llm_cfg.get("api_base_url", "https://api.openai.com/v1")
        model = llm_cfg.get("model", "gpt-4o")
        temperature = llm_cfg.get("temperature", 0.7)
        max_tokens = llm_cfg.get("max_tokens", 4000)
        timeout = llm_cfg.get("timeout", 60)

    # 防止 max_tokens 被误设为模型上下文窗口大小等超大值
    max_tokens = min(max_tokens, 16384)

    # 对数据库字段做长度限制，防止提示注入
    def _safe(text: str, max_len: int = 500) -> str:
        return str(text)[:max_len].replace("{", "{{").replace("}", "}}")

    # 预计算报价，用于模板
    hour_record = db.query(Hour).filter(Hour.value == hour, Hour.is_active == True).first()
    rate = hour_record.unit_price if hour_record and hour_record.unit_price else 2000
    total_cost = rate * hour

    # 预计算课时分块
    hour_block1 = max(1, hour // 8)
    hour_block2 = max(1, hour // 8)
    hour_block3 = hour // 2
    hour_block4 = hour - hour_block1 - hour_block2 - hour_block3

    # 优先从数据库读取活跃提示词模板
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

    try:
        if api_key and api_key != "sk-xxx":
            # 自动补全 /v1 路径：兼容用户填写域名或完整 URL 两种情况
            base = api_base_url.rstrip("/")
            if not base.endswith("/v1"):
                base = f"{base}/v1"
            response = httpx.post(
                f"{base}/chat/completions",
                headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
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
                # 记录 token 消耗
                usage = result.get("usage", {})
                if llm_config_id:
                    log = TokenUsageLog(
                        llm_config_id=llm_config_id,
                        model=model,
                        prompt_tokens=usage.get("prompt_tokens", 0),
                        completion_tokens=usage.get("completion_tokens", 0),
                        total_tokens=usage.get("total_tokens", 0),
                    )
                    db.add(log)

                # 解析 LLM 返回的 JSON
                plan_json = _parse_llm_json(content)
                if plan_json is not None:
                    _normalize_title_subtitle(plan_json, enterprise_name)
                    plan_json["deliverables"] = DELIVERABLES
                    plan_json["pricing"] = {
                        "hour": hour,
                        "unit_price": rate,
                        "total_cost": total_cost,
                    }
                    # 持久化 AI 生成的方案
                    plan_record = GeneratedPlan(
                        major=major,
                        industry=industry,
                        enterprise=enterprise_name,
                        province=region,
                        hour=hour,
                        source="ai",
                        plan_title=plan_json.get("title", ""),
                        plan_data=json.dumps(plan_json, ensure_ascii=False),
                        client_request_id=client_request_id,
                    )
                    db.add(plan_record)
                    try:
                        db.commit()
                    except Exception:
                        db.rollback()
                        raise
                    result = {"data": plan_json, "source": "ai"}
                    if client_request_id:
                        result["client_request_id"] = client_request_id
                    return result
                else:
                    _logger.warning("LLM 返回 JSON 解析失败，回退到模板")
            else:
                _logger.warning("LLM API 返回非 200 状态码: %d, body: %s",
                                response.status_code, response.text[:500])
    except Exception as e:
        _logger.error("AI API call failed: %s", e)

    # 回退到模板生成（JSON 格式）
    fallback = _build_fallback_json(enterprise_name, major, industry,
                                    hour, hour_block1, hour_block2,
                                    hour_block3, hour_block4,
                                    rate, total_cost)
    # 持久化模板回退的方案
    plan_record = GeneratedPlan(
        major=major,
        industry=industry,
        enterprise=enterprise_name,
        province=region,
        hour=hour,
        source="template",
        plan_title=fallback.get("title", ""),
        plan_data=json.dumps(fallback, ensure_ascii=False),
        client_request_id=client_request_id,
    )
    db.add(plan_record)
    try:
        db.commit()
    except Exception:
        db.rollback()
        raise
    result = {"data": fallback, "source": "template", "llm_error": "大模型调用失败，已使用模板生成方案。请检查大模型配置（API Key、Base URL）是否正确。"}
    if client_request_id:
        result["client_request_id"] = client_request_id
    return result


@router.get("/api/generate/status/{client_request_id}", response_model=GenerateStatusResponse)
def get_generate_status(client_request_id: str, db: Session = Depends(get_db)):
    """查询生成任务状态。"""
    # 验证 UUID 格式
    try:
        uuid.UUID(client_request_id)
    except (ValueError, TypeError):
        raise HTTPException(status_code=400, detail="client_request_id 不是合法的 UUID 格式")

    plan = db.query(GeneratedPlan).filter(
        GeneratedPlan.client_request_id == client_request_id
    ).first()

    if plan:
        # 尝试解析已有的方案数据
        try:
            plan_json = json.loads(plan.plan_data)
        except (json.JSONDecodeError, TypeError):
            plan_json = None

        if plan_json:
            # 已成功生成的方案始终可查，不受过期限制
            return GenerateStatusResponse(status="completed", data=plan_json, source=plan.source)

        # 尚未生成完成的方案，超过 5 分钟视为过期
        now = datetime.now(timezone.utc)
        plan_time = plan.created_at.replace(tzinfo=timezone.utc) if plan.created_at.tzinfo is None else plan.created_at
        if now - plan_time > timedelta(minutes=5):
            return GenerateStatusResponse(status="expired", message="生成超时")

        return GenerateStatusResponse(status="pending")

    # 没有找到记录，视为 pending（记录可能尚未创建）
    return GenerateStatusResponse(status="pending")
