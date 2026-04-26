import json
from datetime import datetime, timedelta, timezone
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import or_
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import get_current_user
from app.models.generated_plan import GeneratedPlan
from app.utils.datetime import utc_isoformat

router = APIRouter(prefix="/api/admin/plans", tags=["admin-plans"])


@router.get("/filter-options")
def get_filter_options(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """返回方案表中去重的 major / industry / province 值列表"""
    majors = (
        db.query(GeneratedPlan.major)
        .filter(GeneratedPlan.major != "", GeneratedPlan.major.isnot(None))
        .distinct()
        .order_by(GeneratedPlan.major)
        .all()
    )
    industries = (
        db.query(GeneratedPlan.industry)
        .filter(GeneratedPlan.industry != "", GeneratedPlan.industry.isnot(None))
        .distinct()
        .order_by(GeneratedPlan.industry)
        .all()
    )
    provinces = (
        db.query(GeneratedPlan.province)
        .filter(GeneratedPlan.province != "", GeneratedPlan.province.isnot(None))
        .distinct()
        .order_by(GeneratedPlan.province)
        .all()
    )
    return {
        "majors": [r[0] for r in majors],
        "industries": [r[0] for r in industries],
        "provinces": [r[0] for r in provinces],
    }


@router.get("")
def list_plans(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    source: Optional[str] = None,
    major: Optional[str] = None,
    industry: Optional[str] = None,
    province: Optional[str] = None,
    keyword: Optional[str] = None,
    date_from: Optional[str] = None,
    date_to: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    query = db.query(GeneratedPlan)

    if source:
        query = query.filter(GeneratedPlan.source == source)

    if major:
        query = query.filter(GeneratedPlan.major == major)

    if industry:
        query = query.filter(GeneratedPlan.industry == industry)

    if province:
        query = query.filter(GeneratedPlan.province == province)

    if keyword:
        pattern = f"%{keyword}%"
        query = query.filter(
            or_(
                GeneratedPlan.plan_title.like(pattern),
                GeneratedPlan.major.like(pattern),
                GeneratedPlan.industry.like(pattern),
                GeneratedPlan.enterprise.like(pattern),
            )
        )

    if date_from:
        try:
            dt_from = datetime.fromisoformat(date_from)
            if dt_from.tzinfo is None:
                dt_from = dt_from.replace(tzinfo=timezone.utc)
            query = query.filter(GeneratedPlan.created_at >= dt_from)
        except (ValueError, TypeError):
            pass

    if date_to:
        try:
            dt_to = datetime.fromisoformat(date_to)
            if dt_to.tzinfo is None:
                dt_to = dt_to.replace(tzinfo=timezone.utc)
            # 包含 date_to 当天：小于 date_to 的下一天
            dt_to_end = dt_to + timedelta(days=1)
            query = query.filter(GeneratedPlan.created_at < dt_to_end)
        except (ValueError, TypeError):
            pass

    total = query.count()
    items = (
        query.order_by(GeneratedPlan.created_at.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
        .all()
    )

    return {
        "items": [
            {
                "id": p.id,
                "major": p.major or "",
                "industry": p.industry or "",
                "enterprise": p.enterprise or "",
                "province": p.province or "",
                "hour": p.hour,
                "source": p.source or "",
                "plan_title": p.plan_title or "",
                "created_at": utc_isoformat(p.created_at),
            }
            for p in items
        ],
        "total": total,
        "page": page,
        "page_size": page_size,
    }


@router.get("/{plan_id}")
def get_plan(
    plan_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    plan = db.query(GeneratedPlan).filter(GeneratedPlan.id == plan_id).first()
    if not plan:
        raise HTTPException(status_code=404, detail="方案不存在")

    plan_data = None
    if plan.plan_data:
        try:
            plan_data = json.loads(plan.plan_data)
        except (json.JSONDecodeError, TypeError):
            plan_data = plan.plan_data

    return {
        "id": plan.id,
        "major": plan.major or "",
        "industry": plan.industry or "",
        "enterprise": plan.enterprise or "",
        "province": plan.province or "",
        "hour": plan.hour,
        "source": plan.source or "",
        "plan_title": plan.plan_title or "",
        "plan_data": plan_data,
        "created_at": utc_isoformat(plan.created_at),
    }


@router.delete("/{plan_id}")
def delete_plan(
    plan_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    plan = db.query(GeneratedPlan).filter(GeneratedPlan.id == plan_id).first()
    if not plan:
        raise HTTPException(status_code=404, detail="方案不存在")

    db.delete(plan)
    db.commit()
    return {"message": "删除成功"}
