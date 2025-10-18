from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
from app.models import CategoryEnum, LeadStatus


class VenueBase(BaseModel):
    name: str
    category: Optional[CategoryEnum] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    address: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    website: Optional[str] = None


class VenueCreate(VenueBase):
    pass


class VenueResponse(VenueBase):
    id: int
    score: Optional[float] = None
    lead_status: Optional[LeadStatus] = None
    ai_description: Optional[str] = None
    ai_outreach_message: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True


class ParsingRequest(BaseModel):
    region: str = "Алматы"
    query: str = "глэмпинг"
    limit: int = 50