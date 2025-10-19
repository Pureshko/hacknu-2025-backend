from sqlalchemy import (
    Column, Integer, String, Float, DateTime, JSON, 
    Enum, Text, Boolean, Index
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
    name = Column(String(500), nullable=False, index=True)
    accommodation_type = Column(Enum(AccommodationType), index=True)
    description = Column(Text)
    ai_generated_description = Column(Text)
    
    # Location
    latitude = Column(Float)
    longitude = Column(Float)
    address = Column(String(1000))
    region = Column(String(200), index=True)
    
    # Contact info
    phone = Column(String(50))
    email = Column(String(255))
    website = Column(String(500))
    instagram = Column(String(255))
    telegram = Column(String(255))
    whatsapp = Column(String(50))
    
    # Business details
    room_count = Column(Integer)
    price_min = Column(Float)
    price_max = Column(Float)
    amenities = Column(JSON)
    
    # Media
    photos = Column(JSON)
    
    # Reviews and ratings
    rating = Column(Float)
    review_count = Column(Integer)
    reviews = Column(JSON)
    
    # Priority and analysis
    priority_score = Column(Float, index=True)
    lead_status = Column(Enum(LeadStatus), index=True)
    verification_status = Column(
        Enum(VerificationStatus), 
        default=VerificationStatus.NEW,
        index=True
    )
    
    # Analytics metrics
    online_activity_score = Column(Float)
    data_completeness_score = Column(Float)
    popularity_score = Column(Float)
    commercial_potential_score = Column(Float)
    
    # Source tracking - UNIQUE constraints for deduplication
    data_sources = Column(JSON)
    twogis_id = Column(String(100), unique=True, index=True, nullable=True)
    google_place_id = Column(String(255), unique=True, index=True, nullable=True)
    
    # Outreach
    outreach_template = Column(Text)
    outreach_sent = Column(Boolean, default=False)
    outreach_response = Column(Text)
    
    # Timestamps
    created_at = Column(
        DateTime(timezone=True), 
        server_default=func.now(),
        nullable=False
    )
    updated_at = Column(
        DateTime(timezone=True), 
        onupdate=func.now()
    )
    last_checked_at = Column(DateTime(timezone=True))
    
    # Composite indexes for common queries
    __table_args__ = (
        Index('ix_accommodation_region_type', 'region', 'accommodation_type'),
        Index('ix_accommodation_priority_status', 'priority_score', 'lead_status'),
    )