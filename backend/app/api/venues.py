from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from app.database import get_db
from app.models import Venue, LeadStatus, CategoryEnum
from app.schemas import VenueResponse, VenueCreate
from app.ai.scoring_agent import ScoringAgent
from app.ai.description_gen import DescriptionGenerator, OutreachGenerator
from sqlalchemy import func

router = APIRouter(prefix="/venues", tags=["venues"])

scoring_agent = ScoringAgent()
description_gen = DescriptionGenerator()
outreach_gen = OutreachGenerator()


@router.get("/", response_model=List[VenueResponse])
async def get_venues(
    skip: int = 0,
    limit: int = 100,
    lead_status: Optional[LeadStatus] = None,
    category: Optional[CategoryEnum] = None,
    min_score: Optional[float] = None,
    db: Session = Depends(get_db),
):
    """Получить список объектов с фильтрами"""
    query = db.query(Venue)

    if lead_status:
        query = query.filter(Venue.lead_status == lead_status)
    if category:
        query = query.filter(Venue.category == category)
    if min_score:
        query = query.filter(Venue.score >= min_score)

    venues = query.order_by(Venue.score.desc()).offset(skip).limit(limit).all()
    return venues


@router.get("/{venue_id}", response_model=VenueResponse)
async def get_venue(venue_id: int, db: Session = Depends(get_db)):
    """Получить один объект по ID"""
    venue = db.query(Venue).filter(Venue.id == venue_id).first()
    if not venue:
        raise HTTPException(status_code=404, detail="Venue not found")
    return venue


@router.post("/{venue_id}/generate-content")
async def generate_content(venue_id: int, db: Session = Depends(get_db)):
    """Генерирует AI-описание и outreach сообщение для объекта"""
    venue = db.query(Venue).filter(Venue.id == venue_id).first()
    if not venue:
        raise HTTPException(status_code=404, detail="Venue not found")

    venue_data = {
        "name": venue.name,
        "category": venue.category,
        "address": venue.address,
        "description": venue.description,
        "amenities": venue.amenities or [],
    }

    # Генерируем описание и сообщение
    ai_description = await description_gen.generate_description(venue_data)
    ai_outreach = await outreach_gen.generate_outreach(
        venue_data, channel="whatsapp"
    )

    # Обновляем в БД
    venue.ai_description = ai_description
    venue.ai_outreach_message = ai_outreach
    db.commit()

    return {
        "ai_description": ai_description,
        "ai_outreach_message": ai_outreach,
    }


@router.post("/{venue_id}/rescore")
async def rescore_venue(venue_id: int, db: Session = Depends(get_db)):
    """Пересчитать скор объекта"""
    venue = db.query(Venue).filter(Venue.id == venue_id).first()
    if not venue:
        raise HTTPException(status_code=404, detail="Venue not found")

    venue_data = {
        "name": venue.name,
        "category": venue.category,
        "phone": venue.phone,
        "email": venue.email,
        "website": venue.website,
        "instagram": venue.instagram,
        "photos": venue.photos,
        "rating": venue.rating,
        "reviews_count": venue.reviews_count,
        "description": venue.description,
        "price_min": venue.price_min,
        "price_max": venue.price_max,
    }

    score, lead_status = await scoring_agent.score_venue(venue_data)

    venue.score = score
    venue.lead_status = lead_status
    db.commit()

    return {"score": score, "lead_status": lead_status}


@router.get("/stats/summary")
async def get_stats(db: Session = Depends(get_db)):
    """Получить статистику по объектам"""
    total = db.query(Venue).count()
    hot_leads = (
        db.query(Venue).filter(Venue.lead_status == LeadStatus.HOT).count()
    )
    warm_leads = (
        db.query(Venue).filter(Venue.lead_status == LeadStatus.WARM).count()
    )
    cold_leads = (
        db.query(Venue).filter(Venue.lead_status == LeadStatus.COLD).count()
    )

    avg_score = db.query(Venue).with_entities(
        func.avg(Venue.score)
    ).scalar() or 0

    return {
        "total": total,
        "hot_leads": hot_leads,
        "warm_leads": warm_leads,
        "cold_leads": cold_leads,
        "avg_score": round(float(avg_score), 2),
    }