from datetime import datetime, timedelta
from sqlalchemy import func
from sqlalchemy.orm import Session
from app.models.analytics import VisitLog
from app.models.enterprise import Enterprise


def get_summary(db: Session):
    total_visits = db.query(VisitLog).count()
    total_enterprises = db.query(Enterprise).count()

    today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
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
    """按天统计访问量趋势"""
    today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    start = today - timedelta(days=days)

    results = db.query(
        func.strftime('%Y-%m-%d', VisitLog.request_timestamp).label("date"),
        func.count(VisitLog.id).label("count")
    ).filter(
        VisitLog.request_timestamp >= start
    ).group_by(
        func.strftime('%Y-%m-%d', VisitLog.request_timestamp)
    ).order_by("date").all()

    return [{"date": str(r.date), "count": r.count} for r in results]


def get_province_distribution(db: Session, days: int = 30):
    today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
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
    today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
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
    today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
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
