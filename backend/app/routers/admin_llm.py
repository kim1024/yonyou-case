import httpx
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, case, cast, Date
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime, timedelta, timezone, date
from app.utils.datetime import utc_isoformat
from app.database import get_db
from app.models.llm_config import LLMConfig
from app.models.token_usage_log import TokenUsageLog
from app.dependencies import get_current_user

router = APIRouter(prefix="/api/admin/llm", tags=["llm-configs"])


# ─── API Key 脱敏工具 ──────────────────────────────────────────────────────────

def mask_api_key(key: str) -> str:
    """对 API Key 进行脱敏处理：前4位 + *** + 后4位。"""
    if not key or len(key) < 9:
        return "***"
    return f"{key[:4]}***{key[-4:]}"


# ─── Pydantic 模型 ─────────────────────────────────────────────────────────────

class LLMConfigCreate(BaseModel):
    name: str
    api_base_url: str
    api_key: str
    model: str
    temperature: float = 0.7
    max_tokens: int = Field(default=2000, ge=1, le=16384)
    timeout: int = 60
    is_active: bool = False


class LLMConfigUpdate(BaseModel):
    name: Optional[str] = None
    api_base_url: Optional[str] = None
    api_key: Optional[str] = Field(default=None, description="传空字符串则不更新")
    model: Optional[str] = None
    temperature: Optional[float] = None
    max_tokens: Optional[int] = Field(default=None, ge=1, le=16384)
    timeout: Optional[int] = None
    is_active: Optional[bool] = None


class ModelStats(BaseModel):
    model: str
    total_tokens: int
    calls: int


class DailyTrend(BaseModel):
    date: str
    tokens: int
    calls: int


class FetchModelsRequest(BaseModel):
    api_base_url: str
    api_key: str


class TokenStatsResponse(BaseModel):
    total_tokens: int
    total_calls: int
    today_tokens: int
    today_calls: int
    avg_tokens_per_call: int
    by_model: List[ModelStats]
    daily_trend: List[DailyTrend]


# ─── LLM 配置 CRUD ─────────────────────────────────────────────────────────────

@router.get("/configs")
def list_configs(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """列出所有大模型配置（分页），API Key 脱敏显示。"""
    total = db.query(LLMConfig).count()
    items = (
        db.query(LLMConfig)
        .order_by(LLMConfig.id.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
        .all()
    )
    return {
        "items": [
            {
                "id": c.id,
                "name": c.name,
                "api_base_url": c.api_base_url,
                "api_key_masked": mask_api_key(c.api_key),
                "model": c.model,
                "temperature": c.temperature,
                "max_tokens": c.max_tokens,
                "timeout": c.timeout,
                "is_active": c.is_active,
                "created_at": utc_isoformat(c.created_at),
                "updated_at": utc_isoformat(c.updated_at),
            }
            for c in items
        ],
        "total": total,
        "page": page,
        "page_size": page_size,
    }


@router.post("/configs")
def create_config(data: LLMConfigCreate, db: Session = Depends(get_db), current_user: dict = Depends(get_current_user)):
    """新建大模型配置。若标记为 is_active=True，先将其他配置设为非激活。"""
    if data.is_active:
        db.query(LLMConfig).filter(LLMConfig.is_active == True).update({"is_active": False})

    config = LLMConfig(**data.model_dump())
    db.add(config)
    db.commit()
    db.refresh(config)
    return {"id": config.id, "message": "创建成功"}


@router.put("/configs/{config_id}")
def update_config(config_id: int, data: LLMConfigUpdate, db: Session = Depends(get_db), current_user: dict = Depends(get_current_user)):
    """更新大模型配置。api_key 传空字符串则跳过；更新为 is_active=True 时先将其他配置设为非激活。"""
    config = db.query(LLMConfig).filter(LLMConfig.id == config_id).first()
    if not config:
        raise HTTPException(status_code=404, detail="配置不存在")

    update_data = data.model_dump(exclude_unset=True)

    # api_key 为空字符串时跳过更新
    if "api_key" in update_data and update_data["api_key"] == "":
        del update_data["api_key"]

    # 若标记为激活，先将其他配置取消激活
    if update_data.get("is_active"):
        db.query(LLMConfig).filter(
            LLMConfig.is_active == True, LLMConfig.id != config_id
        ).update({"is_active": False})

    for key, value in update_data.items():
        setattr(config, key, value)

    db.commit()
    return {"message": "更新成功"}


@router.delete("/configs/{config_id}")
def delete_config(config_id: int, db: Session = Depends(get_db), current_user: dict = Depends(get_current_user)):
    """删除大模型配置。若删除的是当前激活配置，返回警告但不阻止删除。"""
    config = db.query(LLMConfig).filter(LLMConfig.id == config_id).first()
    if not config:
        raise HTTPException(status_code=404, detail="配置不存在")

    was_active = config.is_active
    db.delete(config)
    db.commit()

    if was_active:
        return {"message": "删除成功", "warning": "删除了当前激活的配置，无可用激活配置"}
    return {"message": "删除成功"}


@router.post("/configs/{config_id}/activate")
def activate_config(config_id: int, db: Session = Depends(get_db), current_user: dict = Depends(get_current_user)):
    """激活指定配置，其他配置全部设为非激活。"""
    config = db.query(LLMConfig).filter(LLMConfig.id == config_id).first()
    if not config:
        raise HTTPException(status_code=404, detail="配置不存在")

    # 全部取消激活
    db.query(LLMConfig).filter(LLMConfig.is_active == True).update({"is_active": False})
    # 激活目标
    config.is_active = True
    db.commit()
    return {"message": f"已激活配置「{config.name}」"}


# ─── Token 消耗统计 ─────────────────────────────────────────────────────────────

@router.get("/token-stats")
def get_token_stats(
    days: int = Query(30, ge=1, le=365, description="统计最近 N 天"),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """Token 消耗统计面板。返回近 N 天的汇总数据。"""
    now = datetime.now(timezone.utc)
    start_date = now - timedelta(days=days)
    today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)

    # 基础查询条件
    base_filter = TokenUsageLog.request_timestamp >= start_date
    today_filter = TokenUsageLog.request_timestamp >= today_start

    # 总 token / 总调用
    total_row = (
        db.query(
            func.coalesce(func.sum(TokenUsageLog.total_tokens), 0).label("total_tokens"),
            func.count().label("total_calls"),
        )
        .filter(base_filter)
        .one()
    )
    total_tokens = int(total_row.total_tokens)
    total_calls = int(total_row.total_calls)

    # 今日 token / 今日调用
    today_row = (
        db.query(
            func.coalesce(func.sum(TokenUsageLog.total_tokens), 0).label("today_tokens"),
            func.count().label("today_calls"),
        )
        .filter(today_filter)
        .one()
    )
    today_tokens = int(today_row.today_tokens)
    today_calls = int(today_row.today_calls)

    avg_tokens = total_tokens // total_calls if total_calls > 0 else 0

    # 按模型统计
    by_model_rows = (
        db.query(
            TokenUsageLog.model,
            func.coalesce(func.sum(TokenUsageLog.total_tokens), 0).label("total_tokens"),
            func.count().label("calls"),
        )
        .filter(base_filter)
        .group_by(TokenUsageLog.model)
        .order_by(func.sum(TokenUsageLog.total_tokens).desc())
        .all()
    )
    by_model = [
        {"model": row.model, "total_tokens": int(row.total_tokens), "calls": int(row.calls)}
        for row in by_model_rows
    ]

    # 每日趋势
    daily_rows = (
        db.query(
            cast(TokenUsageLog.request_timestamp, Date).label("date"),
            func.coalesce(func.sum(TokenUsageLog.total_tokens), 0).label("tokens"),
            func.count().label("calls"),
        )
        .filter(base_filter)
        .group_by(cast(TokenUsageLog.request_timestamp, Date))
        .order_by(cast(TokenUsageLog.request_timestamp, Date))
        .all()
    )
    # 补全缺失日期（填 0）
    date_map = {str(row.date): row for row in daily_rows}
    end_date = date.today()
    start_date = end_date - timedelta(days=days)
    daily_trend = []
    for i in range(days + 1):
        d = (start_date + timedelta(days=i)).isoformat()
        row = date_map.get(d)
        daily_trend.append({
            "date": d,
            "tokens": int(row.tokens) if row else 0,
            "calls": int(row.calls) if row else 0,
        })

    return {
        "total_tokens": total_tokens,
        "total_calls": total_calls,
        "today_tokens": today_tokens,
        "today_calls": today_calls,
        "avg_tokens_per_call": avg_tokens,
        "by_model": by_model,
        "daily_trend": daily_trend,
    }


# ─── 模型列表代理 ──────────────────────────────────────────────────────────────

@router.post("/models")
def fetch_models(
    data: FetchModelsRequest,
    current_user: dict = Depends(get_current_user),
):
    """代理请求上游 API 获取可用模型列表，API Key 仅用于代理转发，不记录日志。"""
    # 自动补全 /v1 路径
    base = data.api_base_url.rstrip("/")
    if not base.endswith("/v1"):
        base = f"{base}/v1"

    try:
        response = httpx.get(
            f"{base}/models",
            headers={"Authorization": f"Bearer {data.api_key}"},
            timeout=15,
        )
    except (httpx.ConnectError, httpx.ConnectTimeout, httpx.ReadTimeout) as exc:
        raise HTTPException(status_code=502, detail=f"上游服务连接失败: {exc}")

    if response.status_code != 200:
        raise HTTPException(
            status_code=400,
            detail=f"上游 API 返回错误 (HTTP {response.status_code})",
        )

    try:
        payload = response.json()
    except Exception:
        raise HTTPException(status_code=502, detail="上游 API 响应无法解析为 JSON")

    models = [m["id"] for m in payload.get("data", [])]
    return {"models": sorted(models)}
