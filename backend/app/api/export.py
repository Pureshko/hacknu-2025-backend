from fastapi import APIRouter, Depends, Response
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import Venue
import csv
import json
from io import StringIO

router = APIRouter(prefix="/export", tags=["export"])


@router.get("/csv")
async def export_csv(db: Session = Depends(get_db)):
    """Экспорт в CSV"""
    venues = db.query(Venue).all()

    output = StringIO()
    writer = csv.writer(output)

    # Headers
    writer.writerow([
        "ID",
        "Название",
        "Категория",
        "Адрес",
        "Телефон",
        "Email",
        "Сайт",
        "Instagram",
        "Скор",
        "Статус",
        "AI Описание",
        "Outreach Сообщение",
    ])

    # Data
    for v in venues:
        writer.writerow([
            v.id,
            v.name,
            v.category,
            v.address,
            v.phone,
            v.email,
            v.website,
            v.instagram,
            v.score,
            v.lead_status,
            v.ai_description,
            v.ai_outreach_message,
        ])

    output.seek(0)
    return Response(
        content=output.getvalue(),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=venues.csv"},
    )


@router.get("/json")
async def export_json(db: Session = Depends(get_db)):
    """Экспорт в JSON"""
    venues = db.query(Venue).all()

    data = []
    for v in venues:
        data.append({
            "id": v.id,
            "name": v.name,
            "category": v.category,
            "address": v.address,
            "phone": v.phone,
            "email": v.email,
            "website": v.website,
            "instagram": v.instagram,
            "latitude": v.latitude,
            "longitude": v.longitude,
            "score": v.score,
            "lead_status": v.lead_status,
            "ai_description": v.ai_description,
            "ai_outreach_message": v.ai_outreach_message,
            "amenities": v.amenities,
            "photos": v.photos,
        })

    return Response(
        content=json.dumps(data, ensure_ascii=False, indent=2),
        media_type="application/json",
        headers={"Content-Disposition": "attachment; filename=venues.json"},
    )