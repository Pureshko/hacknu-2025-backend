from fastapi import APIRouter, Depends, BackgroundTasks
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import Venue
from app.schemas import ParsingRequest
from app.parsers.gis2_parser import Gis2Parser
from app.ai.scoring_agent import ScoringAgent
from app.ai.description_gen import DescriptionGenerator
from app.ai.outreach_gen import OutreachGenerator

router = APIRouter(prefix="/parsing", tags=["parsing"])

gis2_parser = Gis2Parser()
scoring_agent = ScoringAgent()
description_gen = DescriptionGenerator()
outreach_gen = OutreachGenerator()


async def parse_and_save_task(
    query: str, region: str, limit: int, db: Session
):
    """Фоновая задача парсинга"""
    venues_data = await gis2_parser.search_venues(query, region, limit)

    for venue_data in venues_data:
        # Проверяем дубликаты
        existing = (
            db.query(Venue).filter(Venue.name == venue_data["name"]).first()
        )
        if existing:
            continue

        # Категоризация
        category = scoring_agent.categorize_venue(venue_data)

        # Скоринг
        score, lead_status = await scoring_agent.score_venue(venue_data)

        # Создаем объект
        venue = Venue(
            name=venue_data["name"],
            address=venue_data["address"],
            latitude=venue_data["latitude"],
            longitude=venue_data["longitude"],
            phone=venue_data.get("phone"),
            website=venue_data.get("website"),
            category=category,
            score=score,
            lead_status=lead_status,
            source=venue_data["source"],
        )

        db.add(venue)

    db.commit()


@router.post("/start")
async def start_parsing(
    request: ParsingRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
):
    """Запустить парсинг в фоне"""
    background_tasks.add_task(
        parse_and_save_task, request.query, request.region, request.limit, db
    )

    return {
        "status": "started",
        "message": f"Парсинг запущен: {request.query} в {request.region}",
    }


@router.post("/generate-all-content")
async def generate_all_content(
    background_tasks: BackgroundTasks, db: Session = Depends(get_db)
):
    """Генерирует контент для всех объектов без AI-описаний"""

    async def generate_task():
        venues = (
            db.query(Venue).filter(Venue.ai_description.is_(None)).all()
        )

        for venue in venues:
            venue_data = {
                "name": venue.name,
                "category": venue.category,
                "address": venue.address,
                "description": venue.description,
                "amenities": venue.amenities or [],
            }

            venue.ai_description = await description_gen.generate_description(
                venue_data
            )
            venue.ai_outreach_message = await outreach_gen.generate_outreach(
                venue_data
            )

        db.commit()

    background_tasks.add_task(generate_task)

    return {"status": "started", "message": "Генерация контента запущена"}