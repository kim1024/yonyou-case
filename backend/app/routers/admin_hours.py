"""课时管理路由 —— CRUD。"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional

from app.database import get_db
from app.models.major import Hour
from app.dependencies import get_current_user

router = APIRouter(prefix="/api/admin/hours", tags=["admin-hours"])


class HourCreate(BaseModel):
    value: int
    label: str = ""
    is_active: bool = True
    sort_order: int = 0


class HourUpdate(BaseModel):
    value: Optional[int] = None
    label: Optional[str] = None
    is_active: Optional[bool] = None
    sort_order: Optional[int] = None


@router.get("")
def list_hours(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    is_active: Optional[bool] = None,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """分页获取课时列表"""
    query = db.query(Hour)
    if is_active is not None:
        query = query.filter(Hour.is_active == is_active)

    total = query.count()
    items = (
        query.order_by(Hour.sort_order, Hour.value)
        .offset((page - 1) * page_size)
        .limit(page_size)
        .all()
    )

    return {
        "items": [
            {
                "id": h.id,
                "value": h.value,
                "label": h.label or f"{h.value}课时",
                "is_active": h.is_active,
                "sort_order": h.sort_order,
            }
            for h in items
        ],
        "total": total,
        "page": page,
        "page_size": page_size,
    }


@router.post("")
def create_hour(
    data: HourCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """新增课时"""
    exists = db.query(Hour).filter(Hour.value == data.value).first()
    if exists:
        raise HTTPException(status_code=400, detail="该课时数已存在")

    hour = Hour(**data.model_dump())
    db.add(hour)
    db.commit()
    db.refresh(hour)
    return {"id": hour.id, "message": "创建成功"}


@router.put("/{hour_id}")
def update_hour(
    hour_id: int,
    data: HourUpdate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """编辑课时"""
    hour = db.query(Hour).filter(Hour.id == hour_id).first()
    if not hour:
        raise HTTPException(status_code=404, detail="课时不存在")

    update_data = data.model_dump(exclude_unset=True)

    if "value" in update_data:
        exists = db.query(Hour).filter(
            Hour.value == update_data["value"], Hour.id != hour_id
        ).first()
        if exists:
            raise HTTPException(status_code=400, detail="该课时数已存在")

    for key, value in update_data.items():
        setattr(hour, key, value)

    db.commit()
    return {"message": "更新成功"}


@router.delete("/{hour_id}")
def delete_hour(
    hour_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """删除课时"""
    hour = db.query(Hour).filter(Hour.id == hour_id).first()
    if not hour:
        raise HTTPException(status_code=404, detail="课时不存在")

    db.delete(hour)
    db.commit()
    return {"message": "删除成功"}
