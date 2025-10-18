from typing import Dict, Any, List


class AnalyzerAgent:
    """Analyzes accommodation data and provides insights"""
    
    def __init__(self):
        pass
    
    def analyze_market(
        self, 
        accommodations: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Analyze market trends and opportunities"""
        
        if not accommodations:
            return {
                "total": 0,
                "by_type": {},
                "by_region": {},
                "avg_priority_score": 0
            }
        
        by_type = {}
        by_region = {}
        total_score = 0
        
        for acc in accommodations:
            # Count by type
            acc_type = acc.get('accommodation_type', 'unknown')
            by_type[acc_type] = by_type.get(acc_type, 0) + 1
            
            # Count by region
            region = acc.get('region', 'unknown')
            by_region[region] = by_region.get(region, 0) + 1
            
            # Sum scores
            total_score += acc.get('priority_score', 0)
        
        return {
            "total": len(accommodations),
            "by_type": by_type,
            "by_region": by_region,
            "avg_priority_score": total_score / len(accommodations)
        }