from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.services import analytics_service
from app.dependencies import get_current_user

router = APIRouter(prefix="/api/admin/analytics", tags=["analytics"])


@router.get("/summary")
def get_summary(db: Session = Depends(get_db), current_user: dict = Depends(get_current_user)):
    return analytics_service.get_summary(db)


@router.get("/visits")
def get_visit_trends(db: Session = Depends(get_db), current_user: dict = Depends(get_current_user)):
    return analytics_service.get_visit_trends(db)


@router.get("/provinces")
def get_province_distribution(db: Session = Depends(get_db), current_user: dict = Depends(get_current_user)):
    return analytics_service.get_province_distribution(db)


@router.get("/case-frequency")
def get_case_frequency(db: Session = Depends(get_db), current_user: dict = Depends(get_current_user)):
    return analytics_service.get_case_frequency(db)


@router.get("/industries")
def get_industry_distribution(db: Session = Depends(get_db), current_user: dict = Depends(get_current_user)):
    return analytics_service.get_industry_distribution(db)
