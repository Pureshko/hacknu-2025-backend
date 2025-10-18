from sqlalchemy import (
    Column, Integer, String, Float, DateTime, JSON, 
    Enum, Text, Boolean
)
from sqlalchemy.sql import func
from ..core.database import Base
import enum


class AccommodationType(str, enum.Enum):
    LUXURY_GLAMPING = "luxury_glamping"
    FAMILY_GUEST_HOUSE = "family_guest_house"
    ECO_TOURISM = "eco_tourism"
    ETHNO_TOURISM = "ethno_tourism"
    MOUNTAIN_HOUSE = "mountain_house"


class LeadStatus(str, enum.Enum):
    HOT = "hot"
    WARM = "warm"
    COLD = "cold"


class VerificationStatus(str, enum.Enum):
    NEW = "new"
    VERIFIED = "verified"
    IN_PROGRESS = "in_progress"


class Accommodation(Base):
    __tablename__ = "accommodations"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Basic info
    name = Column(String, nullable=False, index=True)
    accommodation_type = Column(Enum(AccommodationType))
    description = Column(Text)
    ai_generated_description = Column(Text)
    
    # Location
    latitude = Column(Float)
    longitude = Column(Float)
    address = Column(String)
    region = Column(String, index=True)
    
    # Contact info
    phone = Column(String)
    email = Column(String)
    website = Column(String)
    instagram = Column(String)
    telegram = Column(String)
    whatsapp = Column(String)
    
    # Business details
    room_count = Column(Integer)
    price_min = Column(Float)
    price_max = Column(Float)
    amenities = Column(JSON)  # Wi-Fi, parking, kitchen, etc.
    
    # Media
    photos = Column(JSON)  # List of photo URLs
    
    # Reviews and ratings
    rating = Column(Float)
    review_count = Column(Integer)
    reviews = Column(JSON)
    
    # Priority and analysis
    priority_score = Column(Float, index=True)  # 1-10
    lead_status = Column(Enum(LeadStatus))
    verification_status = Column(Enum(VerificationStatus), 
                                 default=VerificationStatus.NEW)
    
    # Analytics metrics
    online_activity_score = Column(Float)
    data_completeness_score = Column(Float)
    popularity_score = Column(Float)
    commercial_potential_score = Column(Float)
    
    # Source tracking
    data_sources = Column(JSON)  # List of sources where found
    twogis_id = Column(String, unique=True, index=True)
    google_place_id = Column(String)
    
    # Outreach
    outreach_template = Column(Text)
    outreach_sent = Column(Boolean, default=False)
    outreach_response = Column(Text)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), 
                       server_default=func.now())
    updated_at = Column(DateTime(timezone=True), 
                       onupdate=func.now())
    last_checked_at = Column(DateTime(timezone=True))