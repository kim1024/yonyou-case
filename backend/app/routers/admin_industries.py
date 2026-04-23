"""行业管理路由 —— CRUD + 全量列表。"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional

from app.database import get_db
from app.models.major import Industry
from app.models.enterprise import Enterprise
from app.dependencies import get_current_user

router = APIRouter(prefix="/api/admin/industries", tags=["admin-industries"])


class IndustryCreate(BaseModel):
    name: str
    is_active: bool = True
    sort_order: int = 0


class IndustryUpdate(BaseModel):
    name: Optional[str] = None
    is_active: Optional[bool] = None
    sort_order: Optional[int] = None


@router.get("/all")
def list_all_industries(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """返回所有行业列表（不分页，用于下拉选择）"""
    items = (
        db.query(Industry)
        .filter(Industry.is_active == True)
        .order_by(Industry.sort_order, Industry.id)
        .all()
    )
    return [{"id": ind.id, "name": ind.name} for ind in items]


@router.get("")
def list_industries(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    keyword: Optional[str] = None,
    is_active: Optional[bool] = None,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """分页获取行业列表"""
    query = db.query(Industry)
    if keyword:
        query = query.filter(Industry.name.contains(keyword))
    if is_active is not None:
        query = query.filter(Industry.is_active == is_active)

    total = query.count()
    items = (
        query.order_by(Industry.sort_order, Industry.id)
        .offset((page - 1) * page_size)
        .limit(page_size)
        .all()
    )

    return {
        "items": [
            {
                "id": ind.id,
                "name": ind.name,
                "is_active": ind.is_active,
                "sort_order": ind.sort_order,
                "enterprise_count": db.query(Enterprise).filter(Enterprise.industry == ind.name).count(),
            }
            for ind in items
        ],
        "total": total,
        "page": page,
        "page_size": page_size,
    }


@router.post("")
def create_industry(
    data: IndustryCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """新增行业"""
    industry = Industry(**data.model_dump())
    db.add(industry)
    db.commit()
    db.refresh(industry)
    return {"id": industry.id, "message": "创建成功"}


@router.put("/{industry_id}")
def update_industry(
    industry_id: int,
    data: IndustryUpdate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """编辑行业"""
    industry = db.query(Industry).filter(Industry.id == industry_id).first()
    if not industry:
        raise HTTPException(status_code=404, detail="行业不存在")

    update_data = data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(industry, key, value)

    db.commit()
    return {"message": "更新成功"}


@router.delete("/{industry_id}")
def delete_industry(
    industry_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """删除行业"""
    industry = db.query(Industry).filter(Industry.id == industry_id).first()
    if not industry:
        raise HTTPException(status_code=404, detail="行业不存在")

    # 同时删除关联记录
    from app.models.major import MajorIndustry
    db.query(MajorIndustry).filter(MajorIndustry.industry_id == industry_id).delete()

    db.delete(industry)
    db.commit()
    return {"message": "删除成功"}
