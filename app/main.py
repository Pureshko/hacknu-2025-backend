from fastapi import FastAPI, Depends, BackgroundTasks, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from sqlalchemy import func, desc
from typing import Optional, List
import asyncio
import logging
from contextlib import asynccontextmanager

from .core.database import engine, get_db, Base
from .core.config import settings
from .models.accommodation import Accommodation, LeadStatus
from .agents.twogis_agent import TwoGISAgent
from .agents.google_maps_agent import GooglePlacesAgent
from .services.ai_service import AIService
from .services.outreach_service import OutreachService

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


# Lifespan context manager for startup/shutdown
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info("Starting MyTravel AI Agent System")
    Base.metadata.create_all(bind=engine)
    yield
    # Shutdown
    logger.info("Shutting down MyTravel AI Agent System")


app = FastAPI(
    title="MyTravel AI Agent System",
    version="1.0.0",
    lifespan=lifespan
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ==================== HEALTH CHECK ====================
@app.get("/health")
async def health_check(db: Session = Depends(get_db)):
    """Health check endpoint"""
    try:
        # Test DB connection
        db.execute("SELECT 1")
        return {
            "status": "healthy",
            "database": "connected",
            "version": "1.0.0"
        }
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        raise HTTPException(status_code=503, detail="Service unhealthy")


@app.get("/")
async def root():
    return {
        "message": "MyTravel AI Agent System",
        "version": "1.0.0",
        "docs": "/docs"
    }


# ==================== BACKGROUND TASKS ====================
async def scan_region_task(region: str):
    """Background task for scanning region - creates its own DB session"""
    db = next(get_db())
    ai_service = AIService()
    
    try:
        async with TwoGISAgent() as agent:
            logger.info(f"Starting scan for region: {region}")
            accommodations = await agent.search("размещение туристов", region)
            logger.info(f"Found {len(accommodations)} accommodations")
            
            added = 0
            skipped = 0
            
            for acc_data in accommodations:
                try:
                    # Check if exists
                    existing = db.query(Accommodation).filter(
                        Accommodation.twogis_id == acc_data.get("twogis_id")
                    ).first()
                    
                    if existing:
                        skipped += 1
                        continue
                    
                    # Calculate scores
                    scores = ai_service.calculate_priority_score(acc_data)
                    
                    # Generate description
                    if settings.OPENAI_API_KEY:
                        try:
                            description = await ai_service.generate_description(
                                acc_data
                            )
                        except Exception as e:
                            logger.warning(f"AI description failed: {e}")
                            description = ai_service._fallback_description(
                                acc_data
                            )
                    else:
                        description = ai_service._fallback_description(acc_data)
                    
                    # Create record
                    accommodation = Accommodation(
                        name=acc_data.get('name'),
                        twogis_id=acc_data.get('twogis_id'),
                        latitude=acc_data.get('latitude'),
                        longitude=acc_data.get('longitude'),
                        address=acc_data.get('address'),
                        region=acc_data.get('region'),
                        phone=acc_data.get('phone'),
                        website=acc_data.get('website'),
                        accommodation_type=acc_data.get('accommodation_type'),
                        data_sources=acc_data.get('data_sources', []),
                        rating=acc_data.get('rating'),
                        **scores,
                        ai_generated_description=description
                    )
                    
                    db.add(accommodation)
                    db.commit()
                    added += 1
                    
                except Exception as e:
                    logger.error(f"Error processing accommodation: {e}")
                    db.rollback()
                    continue
            
            logger.info(f"Scan complete: {added} added, {skipped} skipped")
            
    except Exception as e:
        logger.error(f"Scan failed: {e}")
    finally:
        db.close()


async def scan_google_places_task(region: str):
    """Background task for Google Places scanning"""
    db = next(get_db())
    ai_service = AIService()
    
    try:
        if not settings.GOOGLE_MAPS_API_KEY:
            logger.error("Google Maps API key not configured")
            return
        
        async with GooglePlacesAgent() as agent:
            logger.info(f"Starting Google Places scan for: {region}")
            accommodations = await agent.search("accommodation", region)
            logger.info(f"Found {len(accommodations)} accommodations")
            
            added = 0
            skipped = 0
            
            for acc_data in accommodations:
                try:
                    # Check if exists
                    existing = db.query(Accommodation).filter(
                        Accommodation.google_place_id == acc_data.get(
                            'google_place_id'
                        )
                    ).first()
                    
                    if existing:
                        skipped += 1
                        continue
                    
                    # Calculate scores
                    scores = ai_service.calculate_priority_score(acc_data)
                    
                    # Generate description
                    if settings.OPENAI_API_KEY:
                        try:
                            description = await ai_service.generate_description(
                                acc_data
                            )
                        except Exception as e:
                            logger.warning(f"AI description failed: {e}")
                            description = ai_service._fallback_description(
                                acc_data
                            )
                    else:
                        description = ai_service._fallback_description(acc_data)
                    
                    # Create record
                    accommodation = Accommodation(
                        name=acc_data.get('name'),
                        google_place_id=acc_data.get('google_place_id'),
                        latitude=acc_data.get('latitude'),
                        longitude=acc_data.get('longitude'),
                        address=acc_data.get('address'),
                        region=acc_data.get('region'),
                        phone=acc_data.get('phone'),
                        website=acc_data.get('website'),
                        accommodation_type=acc_data.get('accommodation_type'),
                        description=acc_data.get('description'),
                        price_min=acc_data.get('price_min'),
                        price_max=acc_data.get('price_max'),
                        photos=acc_data.get('photos', []),
                        rating=acc_data.get('rating'),
                        review_count=acc_data.get('review_count', 0),
                        reviews=acc_data.get('reviews', []),
                        amenities=acc_data.get('amenities', []),
                        data_sources=acc_data.get('data_sources', []),
                        **scores,
                        ai_generated_description=description
                    )
                    
                    db.add(accommodation)
                    db.commit()
                    added += 1
                    
                except Exception as e:
                    logger.error(f"Error processing accommodation: {e}")
                    db.rollback()
                    continue
            
            logger.info(
                f"Google Places scan complete: {added} added, {skipped} skipped"
            )
            
    except Exception as e:
        logger.error(f"Google Places scan failed: {e}")
    finally:
        db.close()


# ==================== SCAN ENDPOINTS ====================
@app.post("/api/scan/start")
async def start_scan(
    region: str = Query("Almaty", description="Region to scan"),
    background_tasks: BackgroundTasks = BackgroundTasks()
):
    """Start scanning for accommodations in 2GIS"""
    background_tasks.add_task(scan_region_task, region)
    return {
        "status": "started",
        "region": region,
        "source": "2gis"
    }


@app.post("/api/scan/google-places")
async def start_google_places_scan(
    region: str = Query("Almaty", description="Region to scan"),
    background_tasks: BackgroundTasks = BackgroundTasks()
):
    """Start scanning Google Places for accommodations"""
    if not settings.GOOGLE_MAPS_API_KEY:
        raise HTTPException(
            status_code=400,
            detail="Google Maps API key not configured"
        )
    
    background_tasks.add_task(scan_google_places_task, region)
    return {
        "status": "started",
        "region": region,
        "source": "google_places"
    }


# ==================== ACCOMMODATION ENDPOINTS ====================
@app.get("/api/accommodations")
async def get_accommodations(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    region: Optional[str] = None,
    accommodation_type: Optional[str] = None,
    lead_status: Optional[LeadStatus] = None,
    min_priority: Optional[float] = Query(None, ge=0, le=10),
    db: Session = Depends(get_db)
):
    """Get accommodations with filters"""
    query = db.query(Accommodation)
    
    if region:
        query = query.filter(Accommodation.region == region)
    
    if accommodation_type:
        query = query.filter(
            Accommodation.accommodation_type == accommodation_type
        )
    
    if lead_status:
        query = query.filter(Accommodation.lead_status == lead_status)
    
    if min_priority is not None:
        query = query.filter(Accommodation.priority_score >= min_priority)
    
    # Order by priority
    query = query.order_by(desc(Accommodation.priority_score))
    
    total = query.count()
    accommodations = query.offset(skip).limit(limit).all()
    
    return {
        "total": total,
        "skip": skip,
        "limit": limit,
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
                "latitude": acc.latitude,
                "longitude": acc.longitude,
            }
            for acc in accommodations
        ]
    }


@app.get("/api/accommodations/{accommodation_id}")
async def get_accommodation(
    accommodation_id: int,
    db: Session = Depends(get_db)
):
    """Get single accommodation details"""
    accommodation = db.query(Accommodation).filter(
        Accommodation.id == accommodation_id
    ).first()
    
    if not accommodation:
        raise HTTPException(status_code=404, detail="Accommodation not found")
    
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
        "review_count": accommodation.review_count,
        "amenities": accommodation.amenities,
        "photos": accommodation.photos,
        "price_min": accommodation.price_min,
        "price_max": accommodation.price_max,
        "data_sources": accommodation.data_sources,
        "created_at": accommodation.created_at,
    }


# ==================== ANALYTICS ENDPOINTS ====================
@app.get("/api/analytics/dashboard")
async def get_dashboard_analytics(db: Session = Depends(get_db)):
    """Get dashboard analytics"""
    
    total = db.query(Accommodation).count()
    
    hot_leads = db.query(Accommodation).filter(
        Accommodation.lead_status == LeadStatus.HOT
    ).count()
    
    by_region = dict(
        db.query(
            Accommodation.region,
            func.count(Accommodation.id)
        ).group_by(Accommodation.region).all()
    )
    
    by_type = dict(
        db.query(
            Accommodation.accommodation_type,
            func.count(Accommodation.id)
        ).group_by(Accommodation.accommodation_type).all()
    )
    
    avg_priority = db.query(
        func.avg(Accommodation.priority_score)
    ).scalar() or 0
    
    return {
        "total_accommodations": total,
        "hot_leads": hot_leads,
        "average_priority_score": round(float(avg_priority), 2),
        "by_region": by_region,
        "by_type": by_type
    }


# ==================== OUTREACH ENDPOINTS ====================
@app.post("/api/accommodations/{accommodation_id}/outreach")
async def generate_outreach(
    accommodation_id: int,
    channel: str = Query("whatsapp", regex="^(whatsapp|email|instagram|telegram)$"),
    db: Session = Depends(get_db)
):
    """Generate outreach message for accommodation"""
    accommodation = db.query(Accommodation).filter(
        Accommodation.id == accommodation_id
    ).first()
    
    if not accommodation:
        raise HTTPException(status_code=404, detail="Accommodation not found")
    
    outreach_service = OutreachService()
    
    acc_dict = {
        "name": accommodation.name,
        "accommodation_type": accommodation.accommodation_type,
        "region": accommodation.region,
        "address": accommodation.address
    }
    
    message = outreach_service.generate_outreach_message(acc_dict, channel)
    
    # Save template
    accommodation.outreach_template = message
    db.commit()
    
    return {
        "message": message,
        "channel": channel
    }


# ==================== EXPORT ENDPOINTS ====================
@app.get("/api/export/csv")
async def export_csv(db: Session = Depends(get_db)):
    """Export accommodations to CSV"""
    import csv
    from io import StringIO
    from fastapi.responses import StreamingResponse
    
    accommodations = db.query(Accommodation).all()
    
    output = StringIO()
    writer = csv.DictWriter(output, fieldnames=[
        "id", "name", "accommodation_type", "region", "address",
        "phone", "email", "website", "priority_score", 
        "lead_status", "rating", "latitude", "longitude",
        "ai_generated_description"
    ])
    
    writer.writeheader()
    for acc in accommodations:
        writer.writerow({
            "id": acc.id or "",
            "name": acc.name or "",
            "accommodation_type": acc.accommodation_type or "",
            "region": acc.region or "",
            "address": acc.address or "",
            "phone": acc.phone or "",
            "email": acc.email or "",
            "website": acc.website or "",
            "priority_score": acc.priority_score or "",
            "lead_status": acc.lead_status or "",
            "rating": acc.rating or "",
            "latitude": acc.latitude or "",
            "longitude": acc.longitude or "",
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