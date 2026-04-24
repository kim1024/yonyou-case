import json
from datetime import timedelta
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import or_
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import get_current_user
from app.models.generated_plan import GeneratedPlan

router = APIRouter(prefix="/api/admin/plans", tags=["admin-plans"])


@router.get("")
def list_plans(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    source: Optional[str] = None,
    keyword: Optional[str] = None,
    date_from: Optional[str] = None,
    date_to: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    query = db.query(GeneratedPlan)

    if source:
        query = query.filter(GeneratedPlan.source == source)

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
        from datetime import datetime as dt
        try:
            dt_from = dt.fromisoformat(date_from)
            query = query.filter(GeneratedPlan.created_at >= dt_from)
        except ValueError:
            pass

    if date_to:
        from datetime import datetime as dt
        try:
            dt_to = dt.fromisoformat(date_to)
            # 包含 date_to 当天：小于 date_to 的下一天
            dt_to_end = dt_to + timedelta(days=1)
            query = query.filter(GeneratedPlan.created_at < dt_to_end)
        except ValueError:
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
                "created_at": p.created_at.isoformat() if p.created_at else None,
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
        "created_at": plan.created_at.isoformat() if plan.created_at else None,
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
