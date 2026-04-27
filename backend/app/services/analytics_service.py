from collections import defaultdict
from datetime import datetime, timedelta, timezone
from sqlalchemy import func
from sqlalchemy.orm import Session
from app.models.analytics import VisitLog
from app.models.enterprise import Enterprise
from app.utils.datetime import SERVER_TIMEZONE, server_today_start_utc, ensure_utc


def get_summary(db: Session):
    total_visits = db.query(VisitLog).count()
    total_enterprises = db.query(Enterprise).count()

    today_start_utc = server_today_start_utc()
    today_visits = db.query(VisitLog).filter(VisitLog.request_timestamp >= today_start_utc).count()

    local_now = datetime.now(timezone.utc).astimezone(SERVER_TIMEZONE)
    week_start_local = (local_now - timedelta(days=local_now.weekday())).replace(
        hour=0, minute=0, second=0, microsecond=0
    )
    week_start_utc = week_start_local.astimezone(timezone.utc)
    week_visits = db.query(VisitLog).filter(VisitLog.request_timestamp >= week_start_utc).count()

    return {
        "total_visits": total_visits,
        "total_enterprises": total_enterprises,
        "today_visits": today_visits,
        "week_visits": week_visits,
    }


def get_visit_trends(db: Session, days: int = 30):
    """按天统计访问量趋势（PV / UV）"""
    end_local = datetime.now(timezone.utc).astimezone(SERVER_TIMEZONE).date()
    start_local = end_local - timedelta(days=days)
    start_utc = datetime.combine(start_local, datetime.min.time(), tzinfo=SERVER_TIMEZONE).astimezone(timezone.utc)

    rows = (
        db.query(VisitLog.request_timestamp, VisitLog.ip_address)
        .filter(VisitLog.request_timestamp >= start_utc)
        .all()
    )

    pv_map: dict[str, int] = defaultdict(int)
    uv_map: dict[str, set[str]] = defaultdict(set)
    for ts, ip in rows:
        utc_ts = ensure_utc(ts)
        if utc_ts is None:
            continue
        day_key = utc_ts.astimezone(SERVER_TIMEZONE).date().isoformat()
        pv_map[day_key] += 1
        if ip:
            uv_map[day_key].add(ip)

    # 补全缺失日期（填 0）
    trend = []
    for i in range(days + 1):
        d = (start_local + timedelta(days=i)).isoformat()
        pv = pv_map.get(d, 0)
        uv = len(uv_map.get(d, set()))
        trend.append({"date": d, "pv": pv, "uv": uv})
    return trend


def get_province_distribution(db: Session, days: int = 30):
    start = server_today_start_utc() - timedelta(days=days)

    results = db.query(
        VisitLog.region,
        func.count(VisitLog.id).label("count")
    ).filter(
        VisitLog.request_timestamp >= start,
        VisitLog.region.isnot(None),
        VisitLog.region != ""
    ).group_by(VisitLog.region).order_by(func.count(VisitLog.id).desc()).limit(20).all()

    return [{"province": r.region, "count": r.count} for r in results]


def get_case_frequency(db: Session, days: int = 30):
    start = server_today_start_utc() - timedelta(days=days)

    results = db.query(
        VisitLog.enterprise,
        VisitLog.industry,
        func.count(VisitLog.id).label("count")
    ).filter(
        VisitLog.request_timestamp >= start,
        VisitLog.enterprise.isnot(None),
        VisitLog.enterprise != ""
    ).group_by(
        VisitLog.enterprise, VisitLog.industry
    ).order_by(func.count(VisitLog.id).desc()).limit(20).all()

    return [{"enterprise": r.enterprise, "industry": r.industry or "", "count": r.count} for r in results]


def get_industry_distribution(db: Session, days: int = 30):
    start = server_today_start_utc() - timedelta(days=days)

    results = db.query(
        VisitLog.industry,
        func.count(VisitLog.id).label("count")
    ).filter(
        VisitLog.request_timestamp >= start,
        VisitLog.industry.isnot(None),
        VisitLog.industry != ""
    ).group_by(VisitLog.industry).order_by(func.count(VisitLog.id).desc()).all()

    return [{"industry": r.industry, "count": r.count} for r in results]
