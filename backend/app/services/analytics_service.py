from datetime import datetime, timedelta, timezone, date
from sqlalchemy import cast, Date, func
from sqlalchemy.orm import Session
from app.models.analytics import VisitLog
from app.models.enterprise import Enterprise


def get_summary(db: Session):
    total_visits = db.query(VisitLog).count()
    total_enterprises = db.query(Enterprise).count()

    today = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)
    today_visits = db.query(VisitLog).filter(VisitLog.request_timestamp >= today).count()

    week_ago = today - timedelta(days=today.weekday())  # 本周一
    week_visits = db.query(VisitLog).filter(VisitLog.request_timestamp >= week_ago).count()

    return {
        "total_visits": total_visits,
        "total_enterprises": total_enterprises,
        "today_visits": today_visits,
        "week_visits": week_visits,
    }


def get_visit_trends(db: Session, days: int = 30):
    """按天统计访问量趋势（PV / UV）"""
    today = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)
    start = today - timedelta(days=days)

    results = db.query(
        cast(VisitLog.request_timestamp, Date).label("date"),
        func.count(VisitLog.id).label("pv"),
        func.count(VisitLog.ip_address.distinct()).label("uv")
    ).filter(
        VisitLog.request_timestamp >= start
    ).group_by(
        cast(VisitLog.request_timestamp, Date)
    ).order_by("date").all()

    # 补全缺失日期（填 0）
    date_map = {str(r.date): (r.pv, r.uv) for r in results}
    end_date = date.today()
    start_date = end_date - timedelta(days=days)
    trend = []
    for i in range(days + 1):
        d = (start_date + timedelta(days=i)).isoformat()
        pv, uv = date_map.get(d, (0, 0))
        trend.append({"date": d, "pv": pv, "uv": uv})
    return trend


def get_province_distribution(db: Session, days: int = 30):
    today = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)
    start = today - timedelta(days=days)

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
    today = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)
    start = today - timedelta(days=days)

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
    today = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)
    start = today - timedelta(days=days)

    results = db.query(
        VisitLog.industry,
        func.count(VisitLog.id).label("count")
    ).filter(
        VisitLog.request_timestamp >= start,
        VisitLog.industry.isnot(None),
        VisitLog.industry != ""
    ).group_by(VisitLog.industry).order_by(func.count(VisitLog.id).desc()).all()

    return [{"industry": r.industry, "count": r.count} for r in results]
