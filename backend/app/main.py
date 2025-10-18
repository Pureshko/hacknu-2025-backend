from fastapi import FastAPI, Depends, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List
import asyncio

from .core.database import engine, get_db, Base
from .core.config import settings
from .models.accommodation import Accommodation
from .agents.twogis_agent import TwoGISAgent
from .services.ai_service import AIService
from .services.outreach_service import OutreachService

# Create tables
Base.metadata.create_all(bind=engine)

app = FastAPI(title="MyTravel AI Agent System")

# CORS - Allow all origins in development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allow all methods
    allow_headers=["*"],  # Allow all headers
)


@app.get("/")
async def root():
    return {"message": "MyTravel AI Agent System"}


@app.post("/api/scan/start")
async def start_scan(
    region: str = "Almaty",
    background_tasks: BackgroundTasks = BackgroundTasks(),
    db: Session = Depends(get_db)
):
    """Start scanning for accommodations"""
    background_tasks.add_task(scan_region, region, db)
    return {"status": "started", "region": region}


async def scan_region(region: str, db: Session):
    """Scan region for accommodations"""
    ai_service = AIService()
    
    async with TwoGISAgent() as agent:
        # Search for accommodations
        accommodations = await agent.search("размещение туристов", region)
        
        for acc_data in accommodations:
            # Check if already exists
            existing = db.query(Accommodation).filter(
                Accommodation.twogis_id == acc_data.get("twogis_id")
            ).first()
            
            if existing:
                continue
            
            # Calculate priority scores
            scores = ai_service.calculate_priority_score(acc_data)
            
            # Generate description (skip if no OpenAI key)
            if settings.OPENAI_API_KEY:
                description = await ai_service.generate_description(acc_data)
            else:
                description = ai_service._fallback_description(acc_data)
            
            # Create accommodation record
            accommodation = Accommodation(
                **{k: v for k, v in acc_data.items() if k in [
                    'name', 'twogis_id', 'latitude', 'longitude', 'address',
                    'region', 'phone', 'website', 'accommodation_type',
                    'data_sources', 'rating'
                ]},
                **scores,
                ai_generated_description=description
            )
            
            db.add(accommodation)
        
        db.commit()


@app.get("/api/accommodations")
async def get_accommodations(
    skip: int = 0,
    limit: int = 50,
    region: str = None,
    db: Session = Depends(get_db)
):
    """Get accommodations"""
    query = db.query(Accommodation)
    
    if region:
        query = query.filter(Accommodation.region == region)
    
    accommodations = query.offset(skip).limit(limit).all()
    
    return {
        "total": query.count(),
        "items": [
            {
                "id": acc.id,
                "name": acc.name,
                "accommodation_type": acc.accommodation_type,
                "region": acc.region,
                "address": acc.address,
                "priority_score": acc.priority_score,
                "lead_status": acc.lead_status,
                "phone": acc.phone,
                "website": acc.website,
                "rating": acc.rating,
            }
            for acc in accommodations
        ]
    }


@app.get("/api/accommodations/{accommodation_id}")
async def get_accommodation(
    accommodation_id: int,
    db: Session = Depends(get_db)
):
    """Get single accommodation"""
    accommodation = db.query(Accommodation).filter(
        Accommodation.id == accommodation_id
    ).first()
    
    if not accommodation:
        return {"error": "Not found"}
    
    return {
        "id": accommodation.id,
        "name": accommodation.name,
        "accommodation_type": accommodation.accommodation_type,
        "description": accommodation.description,
        "ai_generated_description": accommodation.ai_generated_description,
        "latitude": accommodation.latitude,
        "longitude": accommodation.longitude,
        "address": accommodation.address,
        "region": accommodation.region,
        "phone": accommodation.phone,
        "email": accommodation.email,
        "website": accommodation.website,
        "instagram": accommodation.instagram,
        "priority_score": accommodation.priority_score,
        "lead_status": accommodation.lead_status,
        "rating": accommodation.rating,
        "amenities": accommodation.amenities,
        "photos": accommodation.photos,
    }


@app.get("/api/analytics/dashboard")
async def get_dashboard_analytics(db: Session = Depends(get_db)):
    """Get dashboard analytics"""
    
    total = db.query(Accommodation).count()
    hot_leads = db.query(Accommodation).filter(
        Accommodation.lead_status == "hot"
    ).count()
    
    by_region = db.query(
        Accommodation.region,
        func.count(Accommodation.id)
    ).group_by(Accommodation.region).all()
    
    by_type = db.query(
        Accommodation.accommodation_type,
        func.count(Accommodation.id)
    ).group_by(Accommodation.accommodation_type).all()
    
    return {
        "total_accommodations": total,
        "hot_leads": hot_leads,
        "by_region": {region: count for region, count in by_region},
        "by_type": {type_: count for type_, count in by_type}
    }


@app.post("/api/accommodations/{accommodation_id}/outreach")
async def generate_outreach(
    accommodation_id: int,
    channel: str = "whatsapp",
    db: Session = Depends(get_db)
):
    """Generate outreach message"""
    accommodation = db.query(Accommodation).filter(
        Accommodation.id == accommodation_id
    ).first()
    
    if not accommodation:
        return {"error": "Not found"}
    
    outreach_service = OutreachService()
    
    acc_dict = {
        "name": accommodation.name,
        "accommodation_type": accommodation.accommodation_type,
        "region": accommodation.region,
        "address": accommodation.address
    }
    
    message = outreach_service.generate_outreach_message(acc_dict, channel)
    
    accommodation.outreach_template = message
    db.commit()
    
    return {"message": message}


@app.get("/api/export/csv")
async def export_csv(db: Session = Depends(get_db)):
    """Export accommodations to CSV"""
    import csv
    from io import StringIO
    from fastapi.responses import StreamingResponse
    
    accommodations = db.query(Accommodation).all()
    
    output = StringIO()
    writer = csv.DictWriter(output, fieldnames=[
        "name", "accommodation_type", "region", "address",
        "phone", "email", "website", "priority_score", 
        "lead_status", "ai_generated_description"
    ])
    
    writer.writeheader()
    for acc in accommodations:
        writer.writerow({
            "name": acc.name or "",
            "accommodation_type": acc.accommodation_type or "",
            "region": acc.region or "",
            "address": acc.address or "",
            "phone": acc.phone or "",
            "email": acc.email or "",
            "website": acc.website or "",
            "priority_score": acc.priority_score or "",
            "lead_status": acc.lead_status or "",
            "ai_generated_description": acc.ai_generated_description or ""
        })
    
    output.seek(0)
    
    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv",
        headers={
            "Content-Disposition": "attachment; filename=accommodations.csv"
        }
    )

@app.post("/api/scan/google-places")
async def start_google_places_scan(
    region: str = "Almaty",
    background_tasks: BackgroundTasks = BackgroundTasks(),
    db: Session = Depends(get_db)
):
    """Start scanning Google Places for accommodations"""
    background_tasks.add_task(scan_google_places, region, db)
    return {"status": "started", "region": region, "source": "google_places"}


async def scan_google_places(region: str, db: Session):
    """Scan Google Places for accommodations"""
    from .agents.google_maps_agent import GooglePlacesAgent
    
    ai_service = AIService()
    
    async with GooglePlacesAgent() as agent:
        accommodations = await agent.search("accommodation", region)
        
        for acc_data in accommodations:
            # Check if already exists
            existing = db.query(Accommodation).filter(
                Accommodation.google_place_id == acc_data.get('google_place_id')
            ).first()
            
            if existing:
                continue
            
            # Calculate scores
            scores = ai_service.calculate_priority_score(acc_data)
            
            # Generate description
            if settings.OPENAI_API_KEY:
                description = await ai_service.generate_description(acc_data)
            else:
                description = ai_service._fallback_description(acc_data)
            
            # Create record
            accommodation = Accommodation(
                **{k: v for k, v in acc_data.items() if k in [
                    'name', 'google_place_id', 'latitude', 'longitude', 
                    'address', 'region', 'phone', 'website', 
                    'accommodation_type', 'data_sources', 'rating',
                    'description', 'price_min', 'price_max', 'photos',
                    'review_count', 'reviews', 'amenities'
                ]},
                **scores,
                ai_generated_description=description
            )
            
            db.add(accommodation)
        
        db.commit()