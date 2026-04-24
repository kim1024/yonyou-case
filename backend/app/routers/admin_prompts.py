"""提示词模板 CRUD + 版本管理 API。"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func
from pydantic import BaseModel
from typing import Optional
from app.database import get_db
from app.models.prompt_template import PromptTemplate
from app.models.prompt_version import PromptVersion
from app.dependencies import get_current_user

router = APIRouter(prefix="/api/admin/prompts", tags=["prompts"])

# --- 公开接口（无需鉴权）---

public_router = APIRouter(prefix="/api/prompts", tags=["prompts"])


# --- 请求体模型 ---


class PromptTemplateCreate(BaseModel):
    """新建模板请求体。"""
    name: str
    description: Optional[str] = None
    content: str
    variables: Optional[str] = None
    remark: Optional[str] = None


class PromptTemplateUpdate(BaseModel):
    """更新模板基本信息请求体。"""
    name: Optional[str] = None
    description: Optional[str] = None


class PromptVersionCreate(BaseModel):
    """创建新版本请求体。"""
    content: str
    variables: Optional[str] = None
    remark: Optional[str] = None
    created_by: Optional[str] = None


# --- 模板 CRUD ---


@router.get("")
def list_templates(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    keyword: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """获取模板列表（分页）。"""
    query = db.query(PromptTemplate)

    if keyword:
        query = query.filter(PromptTemplate.name.contains(keyword))

    total = query.count()
    items = query.order_by(PromptTemplate.id.desc()).offset((page - 1) * page_size).limit(page_size).all()

    result = []
    for t in items:
        # 获取当前版本信息
        current_version = None
        current_version_number = None
        content_summary = None

        if t.current_version_id:
            current_version = db.query(PromptVersion).filter(PromptVersion.id == t.current_version_id).first()
            if current_version:
                current_version_number = current_version.version_number
                content_summary = current_version.content[:100] if current_version.content else None

        result.append({
            "id": t.id,
            "name": t.name,
            "description": t.description,
            "is_active": t.is_active,
            "current_version_id": t.current_version_id,
            "current_version_number": current_version_number,
            "content_summary": content_summary,
            "created_at": t.created_at.isoformat() if t.created_at else None,
            "updated_at": t.updated_at.isoformat() if t.updated_at else None,
        })

    return {
        "items": result,
        "total": total,
        "page": page,
        "page_size": page_size,
    }


@router.post("")
def create_template(
    data: PromptTemplateCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """新建模板并创建第一个版本。"""
    # 创建模板
    template = PromptTemplate(
        name=data.name,
        description=data.description,
    )
    db.add(template)
    db.flush()  # 获取 template.id

    # 创建第一个版本
    version = PromptVersion(
        template_id=template.id,
        version_number=1,
        content=data.content,
        variables=data.variables,
        remark=data.remark or "初始版本",
        created_by=current_user.get("sub"),
    )
    db.add(version)
    db.flush()

    # 设置当前版本
    template.current_version_id = version.id
    db.commit()
    db.refresh(template)

    return {
        "id": template.id,
        "version_id": version.id,
        "message": "创建成功",
    }


@router.get("/{template_id}")
def get_template(
    template_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """获取模板详情（含当前版本内容）。"""
    template = db.query(PromptTemplate).filter(PromptTemplate.id == template_id).first()
    if not template:
        raise HTTPException(status_code=404, detail="模板不存在")

    current_version = None
    if template.current_version_id:
        current_version = db.query(PromptVersion).filter(PromptVersion.id == template.current_version_id).first()

    return {
        "id": template.id,
        "name": template.name,
        "description": template.description,
        "is_active": template.is_active,
        "current_version_id": template.current_version_id,
        "created_at": template.created_at.isoformat() if template.created_at else None,
        "updated_at": template.updated_at.isoformat() if template.updated_at else None,
        "current_version": {
            "id": current_version.id,
            "version_number": current_version.version_number,
            "content": current_version.content,
            "variables": current_version.variables,
            "remark": current_version.remark,
            "created_by": current_version.created_by,
            "created_at": current_version.created_at.isoformat() if current_version.created_at else None,
        } if current_version else None,
    }


@router.put("/{template_id}")
def update_template(
    template_id: int,
    data: PromptTemplateUpdate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """更新模板基本信息。"""
    template = db.query(PromptTemplate).filter(PromptTemplate.id == template_id).first()
    if not template:
        raise HTTPException(status_code=404, detail="模板不存在")

    update_data = data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(template, key, value)

    db.commit()
    return {"message": "更新成功"}


@router.delete("/{template_id}")
def delete_template(
    template_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """删除模板（级联删除所有版本）。"""
    template = db.query(PromptTemplate).filter(PromptTemplate.id == template_id).first()
    if not template:
        raise HTTPException(status_code=404, detail="模板不存在")

    # 先删除所有版本
    db.query(PromptVersion).filter(PromptVersion.template_id == template_id).delete()
    # 再删除模板
    db.delete(template)
    db.commit()

    return {"message": "删除成功"}


# --- 版本管理 ---


@router.get("/{template_id}/versions")
def list_versions(
    template_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """获取版本列表（按版本号倒序）。"""
    template = db.query(PromptTemplate).filter(PromptTemplate.id == template_id).first()
    if not template:
        raise HTTPException(status_code=404, detail="模板不存在")

    versions = (
        db.query(PromptVersion)
        .filter(PromptVersion.template_id == template_id)
        .order_by(PromptVersion.version_number.desc())
        .all()
    )

    return {
        "items": [
            {
                "id": v.id,
                "version_number": v.version_number,
                "remark": v.remark,
                "created_by": v.created_by,
                "created_at": v.created_at.isoformat() if v.created_at else None,
                "is_current": v.id == template.current_version_id,
            }
            for v in versions
        ]
    }


@router.post("/{template_id}/versions")
def create_version(
    template_id: int,
    data: PromptVersionCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """创建新版本（自动递增版本号并设为当前版本）。"""
    template = db.query(PromptTemplate).filter(PromptTemplate.id == template_id).first()
    if not template:
        raise HTTPException(status_code=404, detail="模板不存在")

    # 获取当前最大版本号
    max_version = (
        db.query(func.max(PromptVersion.version_number))
        .filter(PromptVersion.template_id == template_id)
        .scalar()
    )
    next_version_number = (max_version or 0) + 1

    # 创建新版本
    version = PromptVersion(
        template_id=template_id,
        version_number=next_version_number,
        content=data.content,
        variables=data.variables,
        remark=data.remark,
        created_by=data.created_by or current_user.get("sub"),
    )
    db.add(version)
    db.flush()

    # 将新版本设为当前版本
    template.current_version_id = version.id
    db.commit()
    db.refresh(version)

    return {
        "id": version.id,
        "version_number": version.version_number,
        "message": "版本创建成功",
    }


@router.get("/{template_id}/versions/{version_id}")
def get_version(
    template_id: int,
    version_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """获取版本详情（完整内容）。"""
    version = (
        db.query(PromptVersion)
        .filter(
            PromptVersion.id == version_id,
            PromptVersion.template_id == template_id,
        )
        .first()
    )
    if not version:
        raise HTTPException(status_code=404, detail="版本不存在")

    template = db.query(PromptTemplate).filter(PromptTemplate.id == template_id).first()

    return {
        "id": version.id,
        "version_number": version.version_number,
        "content": version.content,
        "variables": version.variables,
        "remark": version.remark,
        "created_by": version.created_by,
        "created_at": version.created_at.isoformat() if version.created_at else None,
        "is_current": template and version.id == template.current_version_id,
    }


@router.post("/{template_id}/versions/{version_id}/rollback")
def rollback_version(
    template_id: int,
    version_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """回滚到指定版本（将其设为当前版本）。"""
    template = db.query(PromptTemplate).filter(PromptTemplate.id == template_id).first()
    if not template:
        raise HTTPException(status_code=404, detail="模板不存在")

    version = (
        db.query(PromptVersion)
        .filter(
            PromptVersion.id == version_id,
            PromptVersion.template_id == template_id,
        )
        .first()
    )
    if not version:
        raise HTTPException(status_code=404, detail="版本不存在")

    # 将指定版本设为当前版本
    template.current_version_id = version.id
    db.commit()
    db.refresh(template)

    return {
        "message": "回滚成功",
        "current_version_id": template.current_version_id,
        "version_number": version.version_number,
    }


# --- 公开接口 ---


@public_router.get("/active")
def get_active_prompt(
    scene: str = Query(..., description="场景名称"),
    db: Session = Depends(get_db),
):
    """获取当前活跃的提示词（无需鉴权）。"""
    template = (
        db.query(PromptTemplate)
        .filter(
            PromptTemplate.scene == scene,
            PromptTemplate.is_active == True,  # noqa: E712
        )
        .first()
    )

    if not template or not template.current_version_id:
        return None

    version = db.query(PromptVersion).filter(PromptVersion.id == template.current_version_id).first()
    if not version:
        return None

    return {
        "template_id": template.id,
        "name": template.name,
        "scene": template.scene,
        "version_id": version.id,
        "version_number": version.version_number,
        "content": version.content,
        "variables": version.variables,
    }
