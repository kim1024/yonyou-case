"""专业管理路由 —— CRUD + 专业-行业关联管理。"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional

from app.database import get_db
from app.models.major import Major, Industry, MajorIndustry
from app.dependencies import get_current_user

router = APIRouter(prefix="/api/admin/majors", tags=["admin-majors"])


class MajorCreate(BaseModel):
    name: str
    description: str = ""
    icon: str = ""
    is_active: bool = True
    sort_order: int = 0


class MajorUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    icon: Optional[str] = None
    is_active: Optional[bool] = None
    sort_order: Optional[int] = None


class MajorIndustrySet(BaseModel):
    industry_ids: list[int]


@router.get("")
def list_majors(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    keyword: Optional[str] = None,
    is_active: Optional[bool] = None,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """分页获取专业列表"""
    query = db.query(Major)
    if keyword:
        query = query.filter(Major.name.contains(keyword))
    if is_active is not None:
        query = query.filter(Major.is_active == is_active)

    total = query.count()
    items = (
        query.order_by(Major.sort_order, Major.id)
        .offset((page - 1) * page_size)
        .limit(page_size)
        .all()
    )

    return {
        "items": [
            {
                "id": m.id,
                "name": m.name,
                "description": m.description or "",
                "icon": m.icon or "",
                "is_active": m.is_active,
                "sort_order": m.sort_order,
            }
            for m in items
        ],
        "total": total,
        "page": page,
        "page_size": page_size,
    }


@router.post("")
def create_major(
    data: MajorCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """新增专业"""
    # 名称唯一性校验
    exists = db.query(Major).filter(Major.name == data.name).first()
    if exists:
        raise HTTPException(status_code=400, detail="专业名称已存在")

    major = Major(**data.model_dump())
    db.add(major)
    db.commit()
    db.refresh(major)
    return {"id": major.id, "message": "创建成功"}


@router.put("/{major_id}")
def update_major(
    major_id: int,
    data: MajorUpdate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """编辑专业"""
    major = db.query(Major).filter(Major.id == major_id).first()
    if not major:
        raise HTTPException(status_code=404, detail="专业不存在")

    update_data = data.model_dump(exclude_unset=True)

    # 如果修改了名称，校验唯一性
    if "name" in update_data:
        exists = db.query(Major).filter(
            Major.name == update_data["name"], Major.id != major_id
        ).first()
        if exists:
            raise HTTPException(status_code=400, detail="专业名称已存在")

    for key, value in update_data.items():
        setattr(major, key, value)

    db.commit()
    return {"message": "更新成功"}


@router.delete("/{major_id}")
def delete_major(
    major_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """删除专业（同时删除关联记录）"""
    major = db.query(Major).filter(Major.id == major_id).first()
    if not major:
        raise HTTPException(status_code=404, detail="专业不存在")

    # 删除关联的 major_industries 记录
    db.query(MajorIndustry).filter(MajorIndustry.major_id == major_id).delete()
    db.delete(major)
    db.commit()
    return {"message": "删除成功"}


@router.get("/{major_id}/industries")
def get_major_industries(
    major_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """获取某专业关联的行业列表"""
    major = db.query(Major).filter(Major.id == major_id).first()
    if not major:
        raise HTTPException(status_code=404, detail="专业不存在")

    rows = (
        db.query(Industry)
        .join(MajorIndustry, MajorIndustry.industry_id == Industry.id)
        .filter(MajorIndustry.major_id == major_id)
        .order_by(Industry.sort_order, Industry.id)
        .all()
    )
    return [
        {"id": ind.id, "name": ind.name}
        for ind in rows
    ]


@router.post("/{major_id}/industries")
def set_major_industries(
    major_id: int,
    data: MajorIndustrySet,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """设置某专业关联的行业列表（全量替换）"""
    major = db.query(Major).filter(Major.id == major_id).first()
    if not major:
        raise HTTPException(status_code=404, detail="专业不存在")

    # 校验所有 industry_id 是否存在
    if data.industry_ids:
        existing = db.query(Industry.id).filter(Industry.id.in_(data.industry_ids)).all()
        existing_ids = {row[0] for row in existing}
        invalid = set(data.industry_ids) - existing_ids
        if invalid:
            raise HTTPException(status_code=400, detail=f"行业ID不存在: {sorted(invalid)}")

    # 删除旧关联
    db.query(MajorIndustry).filter(MajorIndustry.major_id == major_id).delete()

    # 插入新关联（savepoint 保证原子性）
    savepoint = db.begin_nested()
    try:
        for ind_id in data.industry_ids:
            db.add(MajorIndustry(major_id=major_id, industry_id=ind_id))
        savepoint.commit()
    except Exception:
        savepoint.rollback()
        raise

    db.commit()
    return {"message": "行业关联设置成功"}
