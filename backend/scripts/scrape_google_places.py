import asyncio
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.agents.google_maps_agent import GooglePlacesAgent
from app.core.database import SessionLocal
from app.models.accommodation import Accommodation
from app.services.ai_service import AIService
from app.core.config import settings


async def scrape_google_places():
    """Scrape accommodation data from Google Places API"""
    
    print("Starting Google Places scraping...")
    print(f"API Key: {settings.GOOGLE_MAPS_API_KEY[:10]}...")
    
    db = SessionLocal()
    ai_service = AIService()
    
    try:
        async with GooglePlacesAgent() as agent:
            # Search for accommodations in Almaty
            print("\nSearching for accommodations...")
            accommodations = await agent.search("accommodation", "Almaty")
            
            print(f"\nFound {len(accommodations)} accommodations")
            
            for i, acc_data in enumerate(accommodations, 1):
                print(f"\nProcessing {i}/{len(accommodations)}: {acc_data.get('name')}")
                
                # Check if already exists
                existing = db.query(Accommodation).filter(
                    Accommodation.google_place_id == acc_data.get('google_place_id')
                ).first()
                
                if existing:
                    print(f"  ✓ Already exists, skipping...")
                    continue
                
                # Calculate priority scores
                scores = ai_service.calculate_priority_score(acc_data)
                
                # Generate AI description if OpenAI key is available
                if settings.OPENAI_API_KEY:
                    try:
                        description = await ai_service.generate_description(acc_data)
                        acc_data['ai_generated_description'] = description
                        print(f"  ✓ Generated AI description")
                    except Exception as e:
                        print(f"  ✗ Failed to generate description: {e}")
                        acc_data['ai_generated_description'] = ai_service._fallback_description(acc_data)
                else:
                    acc_data['ai_generated_description'] = ai_service._fallback_description(acc_data)
                
                # Create accommodation record
                accommodation = Accommodation(
                    name=acc_data.get('name'),
                    google_place_id=acc_data.get('google_place_id'),
                    accommodation_type=acc_data.get('accommodation_type'),
                    description=acc_data.get('description'),
                    ai_generated_description=acc_data.get('ai_generated_description'),
                    latitude=acc_data.get('latitude'),
                    longitude=acc_data.get('longitude'),
                    address=acc_data.get('address'),
                    region=acc_data.get('region'),
                    phone=acc_data.get('phone'),
                    website=acc_data.get('website'),
                    price_min=acc_data.get('price_min'),
                    price_max=acc_data.get('price_max'),
                    photos=acc_data.get('photos'),
                    rating=acc_data.get('rating'),
                    review_count=acc_data.get('review_count'),
                    reviews=acc_data.get('reviews'),
                    amenities=acc_data.get('amenities'),
                    data_sources=acc_data.get('data_sources'),
                    online_activity_score=scores.get('online_activity'),
                    data_completeness_score=scores.get('data_completeness'),
                    popularity_score=scores.get('popularity'),
                    commercial_potential_score=scores.get('commercial_potential'),
                    priority_score=scores.get('priority_score'),
                    lead_status=scores.get('lead_status'),
                )
                
                db.add(accommodation)
                db.commit()
                
                print(f"  ✓ Added to database")
                print(f"    Category: {accommodation.accommodation_type}")
                print(f"    Priority: {accommodation.priority_score}/10 ({accommodation.lead_status})")
                print(f"    Rating: {accommodation.rating or 'N/A'}")
            
            print(f"\n✅ Scraping completed! Added {len(accommodations)} accommodations.")
            
    except Exception as e:
        print(f"\n❌ Error during scraping: {e}")
        db.rollback()
    finally:
        db.close()


if __name__ == "__main__":
    asyncio.run(scrape_google_places())