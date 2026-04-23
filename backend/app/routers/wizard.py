import httpx
from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session

from app.config import settings
from app.database import get_db
from app.models.enterprise import Enterprise

router = APIRouter(tags=["wizard"])

MAJORS = ["大数据与会计", "工商企业管理", "市场营销"]
HOURS = [8, 16, 24, 32]


@router.get("/api/majors")
def get_majors():
    return MAJORS


@router.get("/api/industries")
def get_industries(db: Session = Depends(get_db)):
    results = db.query(Enterprise.industry).distinct().all()
    return [r[0] for r in results]


@router.get("/api/config")
def get_config():
    return {
        "title": settings.get("frontend", {}).get("title", "用友产业案例教学项目课程定制系统"),
        "rate_per_hour": settings.get("pricing", {}).get("rate_per_hour", 2000),
    }


@router.post("/api/regions")
def get_regions(request: dict, db: Session = Depends(get_db)):
    industry = request.get("industry")
    results = db.query(Enterprise.province).filter(Enterprise.industry == industry).distinct().all()
    return [r[0] for r in results]


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
def get_hours():
    return HOURS


@router.post("/api/generate")
def generate(request: dict, db: Session = Depends(get_db)):
    major = request.get("major", "")
    industry = request.get("industry", "")
    enterprise_name = request.get("enterprise", "")
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

    prompt = f"""请根据以下信息，生成一份产业案例教学课程设计方案。

专业方向：{major}
行业：{industry}
企业：{enterprise_name}
课时：{hour}课时

企业简介：{company_intro}
用友建设内容：{yonyou_content}

请生成包含以下内容的课程方案：
1. 课程名称
2. 教学目标
3. 教学内容（分章节）
4. 案例分析要点
5. 实践项目设计
6. 考核方式
7. 预估费用（按每课时{settings.get('pricing', {}).get('rate_per_hour', 2000)}元计算）

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
                return {"content": content, "source": "ai"}
    except Exception as e:
        print(f"AI API 调用失败: {e}")

    # 回退到模板生成
    rate = settings.get("pricing", {}).get("rate_per_hour", 2000)
    total_cost = rate * hour
    template = f"""# {enterprise_name} — {major}产业案例教学课程方案

## 一、课程概述

本课程以{enterprise_name}为产业案例，结合{major}专业知识，开展{industry}领域的案例教学。课程总课时{hour}课时，预估费用{total_cost}元。

## 二、企业背景

{enterprise_name}是一家{industry}企业。

{company_intro}

## 三、用友建设内容

{yonyou_content}

## 四、教学目标

1. 掌握{major}专业的核心理论与实践技能
2. 了解{industry}行业的数字化转型实践
3. 学会运用用友产品解决实际业务问题
4. 培养分析问题和解决问题的能力

## 五、教学内容

### 第一阶段：理论基础（{hour//3}课时）
- {industry}行业概述
- {major}专业基础理论
- 数字化转型趋势

### 第二阶段：案例分析（{hour//3}课时）
- {enterprise_name}案例剖析
- 用友解决方案分析
- 同行业案例对比

### 第三阶段：实践操作（{hour - 2*(hour//3)}课时）
- 用友产品实操训练
- 综合项目设计
- 成果汇报与点评

## 六、考核方式

- 案例分析报告：30%
- 实践操作成绩：40%
- 课堂表现：20%
- 出勤率：10%

## 七、费用明细

| 项目 | 金额 |
|------|------|
| 课时费（{hour}课时 × {rate}元） | {total_cost}元 |
| **合计** | **{total_cost}元** |
"""
    return {"content": template, "source": "template"}
