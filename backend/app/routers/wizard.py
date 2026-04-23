import logging
import re
import httpx
from fastapi import APIRouter, HTTPException, Depends, Query
from sqlalchemy.orm import Session

from app.config import settings
from app.database import get_db
from app.models.enterprise import Enterprise
from app.models.major import Major, Industry, MajorIndustry, Region, Hour

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
def get_config():
    return {
        "title": settings.get("frontend", {}).get("title", "用友产业案例教学项目课程定制系统"),
        "rate_per_hour": settings.get("pricing", {}).get("rate_per_hour", 2000),
    }


@router.post("/api/regions")
def get_regions(request: dict, db: Session = Depends(get_db)):
    """获取地区列表（支持按行业筛选，优先从 Region 表查询）"""
    industry = request.get("industry")
    if industry:
        # 从 Region 表查询活跃的地区
        regions = (
            db.query(Region.name)
            .filter(Region.is_active == True)
            .order_by(Region.sort_order, Region.id)
            .all()
        )
        if regions:
            return [r[0] for r in regions]
        # 如果 Region 表为空，回退到 enterprise 表去重查询
        results = db.query(Enterprise.province).filter(
            Enterprise.industry == industry
        ).distinct().all()
        return [r[0] for r in results]
    else:
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
        return [h.value for h in hours]
    # 如果 Hour 表为空，返回默认值
    return [8, 16, 24, 32]


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

    # 尝试调用 AI 大模型
    llm_cfg = settings.get("llm", {})
    api_key = llm_cfg.get("api_key", "")
    api_base_url = llm_cfg.get("api_base_url", "https://api.openai.com/v1")
    model = llm_cfg.get("model", "gpt-4o")

    # 对数据库字段做长度限制，防止提示注入
    def _safe(text: str, max_len: int = 500) -> str:
        return str(text)[:max_len].replace("{", "{{").replace("}", "}}")

    # 预计算报价，用于模板
    rate = settings.get("pricing", {}).get("rate_per_hour", 2000)
    total_cost = rate * hour

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

请严格按照以下格式生成 Markdown 方案，用 **粗体** 标注关键动态信息（如企业名、地区、专业、行业、课时、费用等）：

# {_safe(enterprise_name)}案例教学课程方案

## {_safe(enterprise_name)}

---

## 一、总体介绍
本教学案例基于**{_safe(region)}**地区**{_safe(enterprise_name)}**公司的真实业务场景，结合**{_safe(major)}**专业技术，设计了一套完整的**{hour}课时**教学方案。通过本案例的学习，学员将深入理解**{_safe(industry)}**行业与**{_safe(major)}**技术的融合应用，掌握实际项目中的核心技能。

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

结合**{_safe(industry)}**行业与**{_safe(major)}**专业，学员毕业后可胜任以下岗位：

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

## 最终提交成果物

- 📊 PPT
- 🎬 视频
- 📝 指导书
- 📂 数据集
- 💻 代码包
- 🖥️ 实操环境

---

## 课程最终报价

计价方式：**线性计费**

> 价格 = 课时数 × 2,000 元 = {hour} × 2,000 = **{total_cost:,}元**

<span style="display:block;text-align:center;font-size:48px;font-weight:800;color:var(--color-primary-600);margin:24px 0;letter-spacing:-1px">{total_cost:,}元</span>

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
                    "temperature": llm_cfg.get("temperature", 0.7),
                    "max_tokens": llm_cfg.get("max_tokens", 2000),
                },
                timeout=llm_cfg.get("timeout", 60),
            )
            if response.status_code == 200:
                result = response.json()
                content = result["choices"][0]["message"]["content"]
                # 修复 LLM 可能生成的单 * (italic) 为 ** (bold)
                content = re.sub(r'(?<!\*)\*(?!\s)([^\*]+?)(?<!\s)\*(?!\*)', r'**\1**', content)
                return {"content": content, "source": "ai"}
    except Exception as e:
        _logger.error("AI API call failed: %s", e)

    # 回退到模板生成
    template = f"""# {enterprise_name}案例教学课程方案

## {enterprise_name}

---

## 一、总体介绍

本教学案例基于**{region}**地区**{enterprise_name}**公司的真实业务场景，结合**{major}**专业技术，设计了一套完整的**{hour}课时**教学方案。通过本案例的学习，学员将深入理解**{industry}**行业与**{major}**技术的融合应用，掌握实际项目中的核心技能。

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

结合**{industry}**行业与**{major}**专业，学员毕业后可胜任以下岗位：

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

## 最终提交成果物

- 📊 PPT
- 🎬 视频
- 📝 指导书
- 📂 数据集
- 💻 代码包
- 🖥️ 实操环境

---

## 课程最终报价

计价方式：**线性计费**

> 价格 = 课时数 × 2,000 元 = {hour} × 2,000 = **{total_cost:,}元**

<span style="display:block;text-align:center;font-size:48px;font-weight:800;color:var(--color-primary-600);margin:24px 0;letter-spacing:-1px">{total_cost:,}元</span>

---

> ⚠️ 以上内容由 AI 生成，请结合实际教学需求进行调整。
"""
    return {"content": template, "source": "template"}
