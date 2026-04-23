"""地区管理路由 —— CRUD。"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional

from app.database import get_db
from app.models.major import Region
from app.dependencies import get_current_user

router = APIRouter(prefix="/api/admin/regions", tags=["admin-regions"])


class RegionCreate(BaseModel):
    name: str
    is_active: bool = True
    sort_order: int = 0


class RegionUpdate(BaseModel):
    name: Optional[str] = None
    is_active: Optional[bool] = None
    sort_order: Optional[int] = None


@router.get("")
def list_regions(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    keyword: Optional[str] = None,
    is_active: Optional[bool] = None,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """分页获取地区列表"""
    query = db.query(Region)
    if keyword:
        query = query.filter(Region.name.contains(keyword))
    if is_active is not None:
        query = query.filter(Region.is_active == is_active)

    total = query.count()
    items = (
        query.order_by(Region.sort_order, Region.id)
        .offset((page - 1) * page_size)
        .limit(page_size)
        .all()
    )

    return {
        "items": [
            {
                "id": r.id,
                "name": r.name,
                "is_active": r.is_active,
                "sort_order": r.sort_order,
            }
            for r in items
        ],
        "total": total,
        "page": page,
        "page_size": page_size,
    }


@router.post("")
def create_region(
    data: RegionCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """新增地区"""
    exists = db.query(Region).filter(Region.name == data.name).first()
    if exists:
        raise HTTPException(status_code=400, detail="地区名称已存在")

    region = Region(**data.model_dump())
    db.add(region)
    db.commit()
    db.refresh(region)
    return {"id": region.id, "message": "创建成功"}


@router.put("/{region_id}")
def update_region(
    region_id: int,
    data: RegionUpdate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """编辑地区"""
    region = db.query(Region).filter(Region.id == region_id).first()
    if not region:
        raise HTTPException(status_code=404, detail="地区不存在")

    update_data = data.model_dump(exclude_unset=True)

    if "name" in update_data:
        exists = db.query(Region).filter(
            Region.name == update_data["name"], Region.id != region_id
        ).first()
        if exists:
            raise HTTPException(status_code=400, detail="地区名称已存在")

    for key, value in update_data.items():
        setattr(region, key, value)

    db.commit()
    return {"message": "更新成功"}


@router.delete("/{region_id}")
def delete_region(
    region_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """删除地区"""
    region = db.query(Region).filter(Region.id == region_id).first()
    if not region:
        raise HTTPException(status_code=404, detail="地区不存在")

    db.delete(region)
    db.commit()
    return {"message": "删除成功"}
