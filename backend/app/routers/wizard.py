import logging
import re
import httpx
from fastapi import APIRouter, HTTPException, Depends, Query
from sqlalchemy.orm import Session

from app.config import settings
from app.database import get_db
from app.models.enterprise import Enterprise
from app.models.major import Major, Industry, MajorIndustry, Region, Hour
from app.models.llm_config import LLMConfig
from app.models.prompt_template import PromptTemplate
from app.models.prompt_version import PromptVersion
from app.models.token_usage_log import TokenUsageLog

_logger = logging.getLogger(__name__)

router = APIRouter(tags=["wizard"])


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


@router.post("/api/generate")
def generate(request: dict, db: Session = Depends(get_db)):
    major = request.get("major", "")
    industry = request.get("industry", "")
    enterprise_name = request.get("enterprise", "")
    region = request.get("region", "")
    hour = request.get("hour", 8)

    # 查找企业信息
    enterprise = db.query(Enterprise).filter(
        Enterprise.customer_name == enterprise_name,
        Enterprise.industry == industry
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
        max_tokens = db_llm.max_tokens or 2000
        timeout = db_llm.timeout or 60
        llm_config_id = db_llm.id
    else:
        # fallback 到 config.yaml
        llm_cfg = settings.get("llm", {})
        api_key = llm_cfg.get("api_key", "")
        api_base_url = llm_cfg.get("api_base_url", "https://api.openai.com/v1")
        model = llm_cfg.get("model", "gpt-4o")
        temperature = llm_cfg.get("temperature", 0.7)
        max_tokens = llm_cfg.get("max_tokens", 2000)
        timeout = llm_cfg.get("timeout", 60)

    # 对数据库字段做长度限制，防止提示注入
    def _safe(text: str, max_len: int = 500) -> str:
        return str(text)[:max_len].replace("{", "{{").replace("}", "}}")

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

    # 预计算报价，用于模板
    hour_record = db.query(Hour).filter(Hour.value == hour, Hour.is_active == True).first()
    rate = hour_record.unit_price if hour_record and hour_record.unit_price else 2000
    total_cost = rate * hour

    if db_prompt_content:
        prompt = db_prompt_content.format(
            major=_safe(major),
            industry=_safe(industry),
            enterprise_name=_safe(enterprise_name),
            region=_safe(region),
            hour=hour,
            company_intro=_safe(company_intro, 1000),
            yonyou_content=_safe(yonyou_content, 1000),
            total_cost=f"{total_cost:,}",
        )
    else:
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

请严格按照以下格式生成 Markdown 方案，用 **粗体** 标注关键数字和费用信息：

# {_safe(enterprise_name)}案例教学课程方案

## {_safe(enterprise_name)}

---

## 一、总体介绍
本教学案例基于{_safe(enterprise_name)}公司的真实业务场景，结合{_safe(industry)}专业技术，设计了一套完整的{hour}课时教学方案。通过本案例的学习，学员将深入理解{_safe(industry)}与{_safe(major)}技术的融合应用，掌握实际项目中的核心技能。

## 二、案例课程主要结构

### 模块一：行业背景与需求分析（{max(1, hour // 8)}课时）
- {_safe(industry)}行业现状与发展趋势
- {_safe(enterprise_name)}业务模式与技术需求分析
- 数字化转型痛点与机遇

### 模块二：技术基础与工具介绍（{max(1, hour // 8)}课时）
- {_safe(major)}核心技术原理与架构
- 用友产品体系与解决方案概览
- 开发环境搭建与工具链配置

### 模块三：案例实战与项目实施（{hour // 2}课时）
- {_safe(enterprise_name)}真实业务场景解析
- 基于用友平台的功能开发与集成
- 项目方案设计、实施与优化

### 模块四：总结与拓展（{hour - max(1, hour // 8) - max(1, hour // 8) - hour // 2}课时）
- 项目成果展示与答辩
- {_safe(industry)}领域最佳实践总结
- 职业发展路径与学习资源推荐

## 三、学习后可以胜任的岗位

结合{_safe(industry)}领域与{_safe(major)}专业，学员毕业后可胜任以下岗位：

1. **{_safe(major)}工程师**
   - 负责{_safe(industry)}领域的数据/系统开发
   - 参与企业数字化转型项目
   - 熟练使用用友产品体系

2. **{_safe(industry)}解决方案架构师**
   - 设计行业数字化解决方案
   - 对接客户需求与技术实现

3. **项目实施顾问**
   - 负责用友产品在企业的落地实施
   - 提供客户培训与技术支持

4. **业务分析师**
   - 分析{_safe(industry)}业务流程与需求
   - 设计数字化优化方案

5. **技术项目经理**
   - 管理{_safe(industry)}领域IT项目
   - 协调团队与客户资源

---

<span style="display:block;text-align:center;margin:40px 0 12px;font-size:15px;font-weight:600;color:#888888;letter-spacing:2px">课程最终报价</span>

<span style="display:block;text-align:center;font-size:56px;font-weight:800;letter-spacing:-1px">¥{total_cost:,}</span>

<div style="display:flex;align-items:center;justify-content:center;gap:10px;flex-wrap:wrap;font-size:14px;color:#666666"><span>📊 PPT</span><span>|</span><span>🎬 视频</span><span>|</span><span>📖 指导书</span><span>|</span><span>📂 数据集</span><span>|</span><span>⌨ 代码包</span><span>|</span><span>🖥 实操环境</span></div>

---

> ⚠️ 以上内容由 AI 生成，请结合实际教学需求进行调整。

请使用 Markdown 格式输出。"""

    try:
        if api_key and api_key != "sk-xxx":
            response = httpx.post(
                f"{api_base_url}/chat/completions",
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
                    db.commit()
                # 修复 LLM 可能生成的单 * (italic) 为 ** (bold)
                content = re.sub(r'(?<!\*)\*(?!\s)([^\*]+?)(?<!\s)\*(?!\*)', r'**\1**', content)

                # ========== 标准化报价区域 HTML ==========
                # 将报价标题 span 标准化为前端正则可匹配的格式
                content = re.sub(
                    r'<span\s[^>]*font-size\s*:\s*15px[^>]*>([^<]*最终报价[^<]*)</span>',
                    '<span style="display:block;text-align:center;margin:40px 0 12px;font-size:15px;font-weight:600;color:#888888;letter-spacing:2px">课程最终报价</span>',
                    content,
                )
                # 将报价数字 span 标准化为前端正则可匹配的格式（提取 ¥ 数字部分）
                content = re.sub(
                    r'<span\s[^>]*font-size\s*:\s*56px[^>]*>([¥￥][\d,]+)</span>',
                    '<span style="display:block;text-align:center;font-size:56px;font-weight:800;letter-spacing:-1px">\\1</span>',
                    content,
                )
                # ========== 标准化结束 ==========

                return {"content": content, "source": "ai"}
    except Exception as e:
        _logger.error("AI API call failed: %s", e)

    # 回退到模板生成
    template = f"""# {enterprise_name}案例教学课程方案

## {enterprise_name}

---

## 一、总体介绍

本教学案例基于{enterprise_name}公司的真实业务场景，结合{industry}专业技术，设计了一套完整的**{hour}课时**教学方案。通过本案例的学习，学员将深入理解{industry}与{major}技术的融合应用，掌握实际项目中的核心技能。

## 二、案例课程主要结构

### 模块一：行业背景与需求分析（{max(1, hour // 8)}课时）
- {industry}行业现状与发展趋势
- {enterprise_name}业务模式与技术需求分析
- 数字化转型痛点与机遇

### 模块二：技术基础与工具介绍（{max(1, hour // 8)}课时）
- {major}核心技术原理与架构
- 用友产品体系与解决方案概览
- 开发环境搭建与工具链配置

### 模块三：案例实战与项目实施（{hour // 2}课时）
- {enterprise_name}真实业务场景解析
- 基于用友平台的功能开发与集成
- 项目方案设计、实施与优化

### 模块四：总结与拓展（{hour - max(1, hour // 8) - max(1, hour // 8) - hour // 2}课时）
- 项目成果展示与答辩
- {industry}领域最佳实践总结
- 职业发展路径与学习资源推荐

## 三、学习后可以胜任的岗位

结合{industry}领域与{major}专业，学员毕业后可胜任以下岗位：

1. **{major}工程师**
   - 负责{industry}领域的数据/系统开发
   - 参与企业数字化转型项目
   - 熟练使用用友产品体系

2. **{industry}解决方案架构师**
   - 设计行业数字化解决方案
   - 对接客户需求与技术实现

3. **项目实施顾问**
   - 负责用友产品在企业的落地实施
   - 提供客户培训与技术支持

4. **业务分析师**
   - 分析{industry}业务流程与需求
   - 设计数字化优化方案

5. **技术项目经理**
   - 管理{industry}领域IT项目
   - 协调团队与客户资源

---

<span style="display:block;text-align:center;margin:40px 0 12px;font-size:15px;font-weight:600;color:#888888;letter-spacing:2px">课程最终报价</span>

<span style="display:block;text-align:center;font-size:56px;font-weight:800;letter-spacing:-1px">¥{total_cost:,}</span>

<div style="display:flex;align-items:center;justify-content:center;gap:10px;flex-wrap:wrap;font-size:14px;color:#666666"><span>📊 PPT</span><span>|</span><span>🎬 视频</span><span>|</span><span>📖 指导书</span><span>|</span><span>📂 数据集</span><span>|</span><span>⌨ 代码包</span><span>|</span><span>🖥 实操环境</span></div>

---

> ⚠️ 以上内容由 AI 生成，请结合实际教学需求进行调整。
"""
    return {"content": template, "source": "template"}
