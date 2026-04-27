"""省市管理路由 —— CRUD。"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional

from app.database import get_db
from app.models.province_city import Province, City
from app.models.enterprise import Enterprise
from app.dependencies import get_current_user
from app.utils.datetime import utc_isoformat

router = APIRouter(prefix="/api/admin", tags=["admin-provinces"])


class ProvinceCreate(BaseModel):
    name: str
    is_active: bool = True
    sort_order: int = 0


class ProvinceUpdate(BaseModel):
    name: Optional[str] = None
    is_active: Optional[bool] = None
    sort_order: Optional[int] = None


class CityCreate(BaseModel):
    name: str
    province_id: int
    is_active: bool = True
    sort_order: int = 0


class CityUpdate(BaseModel):
    name: Optional[str] = None
    province_id: Optional[int] = None
    is_active: Optional[bool] = None
    sort_order: Optional[int] = None


# ── 省份 CRUD ──

@router.get("/provinces")
def list_provinces(
    is_active: Optional[bool] = None,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """获取所有省份"""
    query = db.query(Province)
    if is_active is not None:
        query = query.filter(Province.is_active == is_active)

    provinces = query.order_by(Province.sort_order, Province.id).all()

    return {
        "items": [
            {
                "id": p.id,
                "name": p.name,
                "is_active": p.is_active,
                "sort_order": p.sort_order,
                "created_at": utc_isoformat(p.created_at),
                "city_count": len(p.cities),
            }
            for p in provinces
        ],
        "total": len(provinces),
    }


@router.post("/provinces")
def create_province(
    data: ProvinceCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """新增省份"""
    exists = db.query(Province).filter(Province.name == data.name).first()
    if exists:
        raise HTTPException(status_code=400, detail="省份名称已存在")

    province = Province(**data.model_dump())
    db.add(province)
    db.commit()
    db.refresh(province)
    return {"id": province.id, "message": "创建成功"}


@router.put("/provinces/{province_id}")
def update_province(
    province_id: int,
    data: ProvinceUpdate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """编辑省份"""
    province = db.query(Province).filter(Province.id == province_id).first()
    if not province:
        raise HTTPException(status_code=404, detail="省份不存在")

    update_data = data.model_dump(exclude_unset=True)

    if "name" in update_data:
        exists = db.query(Province).filter(
            Province.name == update_data["name"], Province.id != province_id
        ).first()
        if exists:
            raise HTTPException(status_code=400, detail="省份名称已存在")

        # 省份名称变更时，同步更新 enterprises.province
        old_name = province.name
        new_name = update_data["name"]
        if old_name != new_name:
            db.query(Enterprise).filter(Enterprise.province == old_name).update(
                {Enterprise.province: new_name}, synchronize_session="fetch"
            )

    for key, value in update_data.items():
        setattr(province, key, value)

    db.commit()
    return {"message": "更新成功"}


@router.delete("/provinces/{province_id}")
def delete_province(
    province_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """删除省份（级联删除关联城市）"""
    province = db.query(Province).filter(Province.id == province_id).first()
    if not province:
        raise HTTPException(status_code=404, detail="省份不存在")

    # 检查是否有企业引用此省份
    enterprise_count = db.query(Enterprise).filter(
        Enterprise.province == province.name
    ).count()
    if enterprise_count > 0:
        raise HTTPException(
            status_code=400,
            detail=f"该省份被 {enterprise_count} 家企业引用，无法删除。请先迁移企业数据。",
        )

    # SQLAlchemy 的 cascade="all, delete-orphan" 会自动删除关联的城市
    db.delete(province)
    db.commit()
    return {"message": "删除成功"}


@router.get("/provinces/{province_id}/cities")
def list_cities_by_province(
    province_id: int,
    is_active: Optional[bool] = None,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """获取某省份下的城市列表"""
    province = db.query(Province).filter(Province.id == province_id).first()
    if not province:
        raise HTTPException(status_code=404, detail="省份不存在")

    query = db.query(City).filter(City.province_id == province_id)
    if is_active is not None:
        query = query.filter(City.is_active == is_active)

    cities = query.order_by(City.sort_order, City.id).all()

    return {
        "items": [
            {
                "id": c.id,
                "name": c.name,
                "province_id": c.province_id,
                "is_active": c.is_active,
                "sort_order": c.sort_order,
                "created_at": utc_isoformat(c.created_at),
            }
            for c in cities
        ],
        "total": len(cities),
        "province": {"id": province.id, "name": province.name},
    }


# ── 城市 CRUD ──

@router.post("/cities")
def create_city(
    data: CityCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """新增城市"""
    # 验证省份存在
    province = db.query(Province).filter(Province.id == data.province_id).first()
    if not province:
        raise HTTPException(status_code=404, detail="省份不存在")

    # 检查同名城市是否存在
    exists = db.query(City).filter(
        City.name == data.name, City.province_id == data.province_id
    ).first()
    if exists:
        raise HTTPException(status_code=400, detail="该省份下已存在同名城市")

    city = City(**data.model_dump())
    db.add(city)
    db.commit()
    db.refresh(city)
    return {"id": city.id, "message": "创建成功"}


@router.put("/cities/{city_id}")
def update_city(
    city_id: int,
    data: CityUpdate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """编辑城市"""
    city = db.query(City).filter(City.id == city_id).first()
    if not city:
        raise HTTPException(status_code=404, detail="城市不存在")

    update_data = data.model_dump(exclude_unset=True)

    # 如果修改了省份，验证新省份存在
    if "province_id" in update_data:
        province = db.query(Province).filter(Province.id == update_data["province_id"]).first()
        if not province:
            raise HTTPException(status_code=404, detail="省份不存在")

    # 如果修改了名称，检查同名城市是否存在
    if "name" in update_data:
        province_id = update_data.get("province_id", city.province_id)
        exists = db.query(City).filter(
            City.name == update_data["name"],
            City.province_id == province_id,
            City.id != city_id,
        ).first()
        if exists:
            raise HTTPException(status_code=400, detail="该省份下已存在同名城市")

    # 城市名称变更时，同步更新 enterprises.city（需同时匹配省份名称）
    if "name" in update_data:
        old_city_name = city.name
        new_city_name = update_data["name"]
        if old_city_name != new_city_name:
            # 获取当前省份名称（可能已变更省份）
            if "province_id" in update_data:
                target_province = db.query(Province).filter(
                    Province.id == update_data["province_id"]
                ).first()
            else:
                target_province = db.query(Province).filter(
                    Province.id == city.province_id
                ).first()
            province_name = target_province.name

            db.query(Enterprise).filter(
                Enterprise.city == old_city_name,
                Enterprise.province == province_name,
            ).update(
                {Enterprise.city: new_city_name}, synchronize_session="fetch"
            )

    for key, value in update_data.items():
        setattr(city, key, value)

    db.commit()
    return {"message": "更新成功"}


@router.delete("/cities/{city_id}")
def delete_city(
    city_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """删除城市"""
    city = db.query(City).filter(City.id == city_id).first()
    if not city:
        raise HTTPException(status_code=404, detail="城市不存在")

    # 获取省份名称，检查是否有企业引用此城市
    province = db.query(Province).filter(Province.id == city.province_id).first()
    enterprise_count = db.query(Enterprise).filter(
        Enterprise.city == city.name,
        Enterprise.province == province.name,
    ).count()
    if enterprise_count > 0:
        raise HTTPException(
            status_code=400,
            detail=f"该城市被 {enterprise_count} 家企业引用，无法删除。",
        )

    db.delete(city)
    db.commit()
    return {"message": "删除成功"}
