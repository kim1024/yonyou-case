import json
import logging
import uuid
from datetime import datetime, timedelta, timezone
from typing import Optional

from fastapi import APIRouter, HTTPException, Depends, Query, BackgroundTasks
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.config import settings
from app.database import get_db
from app.models.enterprise import Enterprise
from app.models.major import Major, Industry, MajorIndustry, Region, Hour
from app.models.generated_plan import GeneratedPlan
from app.services.generation_service import run_generation_background

_logger = logging.getLogger(__name__)

router = APIRouter(tags=["wizard"])


class GenerateStatusResponse(BaseModel):
    status: str  # "completed" | "pending" | "failed" | "expired"
    data: Optional[dict] = None
    source: Optional[str] = None
    message: Optional[str] = None
    llm_error: Optional[str] = None


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


@router.post("/api/generate", status_code=202)
def generate(request: dict, background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    """接受生成请求，立即返回 202，后台执行生成。"""
    major = request.get("major", "")
    industry = request.get("industry", "")
    enterprise_name = request.get("enterprise", "")
    region = request.get("region", "")
    hour = request.get("hour", 8)

    # 服务端生成 client_request_id（前端未传时）
    client_request_id = request.get("client_request_id")
    if client_request_id:
        try:
            uuid.UUID(str(client_request_id))
        except (ValueError, TypeError):
            client_request_id = str(uuid.uuid4())
    else:
        client_request_id = str(uuid.uuid4())

    # 企业查询（快速校验）
    enterprise = db.query(Enterprise).filter(
        Enterprise.customer_name == enterprise_name,
        Enterprise.industry == industry,
        Enterprise.province == region
    ).first()
    if not enterprise:
        raise HTTPException(status_code=404, detail="未找到匹配的企业信息")

    # 去重检查
    existing = db.query(GeneratedPlan).filter(
        GeneratedPlan.client_request_id == client_request_id,
        GeneratedPlan.status.in_(["pending", "processing", "completed"])
    ).first()
    if existing:
        return {
            "client_request_id": client_request_id,
            "plan_id": existing.id,
            "status": existing.status,
        }

    # DB 层并发控制
    from sqlalchemy import func as sa_func
    active_count = db.query(sa_func.count(GeneratedPlan.id)).filter(
        GeneratedPlan.status.in_(["pending", "processing"])
    ).scalar()
    max_concurrent = 3  # 与原 ConcurrentRequestLimiter 默认值一致
    if active_count >= max_concurrent:
        raise HTTPException(status_code=503, detail="系统繁忙，请稍后重试")

    # Token 限额预检
    try:
        from app.services.llm_runtime import normalize_runtime_state, resolve_runtime_config
        db_llm = normalize_runtime_state(db) or resolve_runtime_config(db)
        if db_llm:
            from app.services.token_quota_service import enforce_quota
            enforce_quota(db, db_llm.id)
    except HTTPException:
        raise
    except Exception:
        pass  # 配置解析失败不阻塞提交，后台任务会再次检查

    # 创建 pending 记录
    plan_record = GeneratedPlan(
        major=major,
        industry=industry,
        enterprise=enterprise_name,
        province=region,
        hour=hour,
        status="pending",
        client_request_id=client_request_id,
    )
    db.add(plan_record)
    db.commit()
    db.refresh(plan_record)

    # 后台执行生成
    background_tasks.add_task(run_generation_background, plan_record.id)

    return {
        "client_request_id": client_request_id,
        "plan_id": plan_record.id,
        "status": "pending",
    }


@router.get("/api/generate/status/{client_request_id}", response_model=GenerateStatusResponse)
def get_generate_status(client_request_id: str, db: Session = Depends(get_db)):
    """查询生成任务状态。"""
    # UUID validation (keep existing)
    try:
        uuid.UUID(client_request_id)
    except (ValueError, TypeError):
        raise HTTPException(status_code=400, detail="client_request_id 不是合法的 UUID 格式")

    plan = db.query(GeneratedPlan).filter(
        GeneratedPlan.client_request_id == client_request_id
    ).first()

    if not plan:
        # Record may not exist yet (just accepted)
        return GenerateStatusResponse(status="pending")

    # Use plan.status field directly
    if plan.status == 'completed':
        try:
            plan_json = json.loads(plan.plan_data)
        except (json.JSONDecodeError, TypeError):
            plan_json = None

        if plan_json:
            llm_error = None
            if plan.source == "template":
                llm_error = "大模型调用失败，已使用模板生成方案。请检查大模型配置是否正确。"
            return GenerateStatusResponse(
                status="completed",
                data=plan_json,
                source=plan.source,
                llm_error=llm_error
            )
        # Completed but no parseable data — treat as failed
        return GenerateStatusResponse(status="failed", message="方案数据异常")

    if plan.status == 'failed':
        return GenerateStatusResponse(
            status="failed",
            message=plan.error_message or "生成失败，请稍后重试"
        )

    # pending or processing — check for timeout
    now = datetime.now(timezone.utc)
    plan_time = plan.started_at or plan.created_at
    if plan_time:
        plan_time = plan_time.replace(tzinfo=timezone.utc) if plan_time.tzinfo is None else plan_time
        if now - plan_time > timedelta(minutes=5):
            # Auto-mark as failed
            plan.status = 'failed'
            plan.error_message = '生成超时'
            db.commit()
            return GenerateStatusResponse(status="expired", message="生成超时")

    return GenerateStatusResponse(status="pending")
