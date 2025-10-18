from typing import Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import func
from ..models.accommodation import Accommodation


class AnalyticsService:
    """Service for analytics and reporting"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def get_dashboard_stats(self) -> Dict[str, Any]:
        """Get dashboard statistics"""
        
        total = self.db.query(Accommodation).count()
        hot_leads = self.db.query(Accommodation).filter(
            Accommodation.lead_status == "hot"
        ).count()
        
        by_region = dict(
            self.db.query(
                Accommodation.region,
                func.count(Accommodation.id)
            ).group_by(Accommodation.region).all()
        )
        
        by_type = dict(
            self.db.query(
                Accommodation.accommodation_type,
                func.count(Accommodation.id)
            ).group_by(Accommodation.accommodation_type).all()
        )
        
        return {
            "total_accommodations": total,
            "hot_leads": hot_leads,
            "by_region": by_region,
            "by_type": by_type
        }
    
    def get_priority_distribution(self) -> Dict[str, int]:
        """Get distribution of priority scores"""
        
        high = self.db.query(Accommodation).filter(
            Accommodation.priority_score >= 8
        ).count()
        
        medium = self.db.query(Accommodation).filter(
            Accommodation.priority_score >= 5,
            Accommodation.priority_score < 8
        ).count()
        
        low = self.db.query(Accommodation).filter(
            Accommodation.priority_score < 5
        ).count()
        
        return {
            "high": high,
            "medium": medium,
            "low": low
        }