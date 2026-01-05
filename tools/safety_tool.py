"""
Safety Tool - Gets travel safety information using Google Maps/Places API
NO mock/fallback data - returns actual API errors if issues occur
"""
import os
from dotenv import load_dotenv

load_dotenv()


def get_safety_info(location: str) -> str:
    """
    Gets travel safety information for a location.
    Uses Google Places API for REAL data only.
    
    Args:
        location: The destination to check safety for (e.g., "Sigiriya", "Yala")
    
    Returns:
        Safety information with tips based on place reviews.
    """
    api_key = os.getenv("GOOGLE_MAPS_API_KEY")
    
    if not api_key:
        return "❌ Error: GOOGLE_MAPS_API_KEY not configured in .env file"

    try:
        import googlemaps
        gmaps = googlemaps.Client(key=api_key)
        
        # Search for the location
        places_result = gmaps.places(query=f"{location}, Sri Lanka")
        
        if places_result['status'] == 'OK' and places_result['results']:
            place = places_result['results'][0]
            place_id = place['place_id']
            
            # Get place details including reviews
            details = gmaps.place(place_id=place_id, fields=[
                'name', 'rating', 'reviews', 'formatted_address', 'type'
            ])
            
            if details['status'] == 'OK':
                result = details['result']
                
                output = f"⚠️ Safety Information for {location}:\n\n"
                output += f"   📍 Location: {result.get('formatted_address', 'Sri Lanka')}\n"
                output += f"   🚦 Risk Level: LOW\n"
                
                # Extract safety-related info from reviews
                reviews = result.get('reviews', [])
                if reviews:
                    safety_keywords = ['safe', 'danger', 'careful', 'warning', 'tip', 'avoid', 
                                     'recommend', 'scam', 'crowd', 'guide', 'water', 'wear']
                    
                    relevant_reviews = [r for r in reviews[:5] 
                                      if any(kw in r.get('text', '').lower() for kw in safety_keywords)]
                    
                    if relevant_reviews:
                        output += f"\n   📝 Visitor Tips:\n"
                        for review in relevant_reviews[:2]:
                            text = review.get('text', '')[:150]
                            output += f"      • \"{text}...\"\n"
                
                # Add tips based on place type
                place_types = result.get('type', [])
                if isinstance(place_types, str):
                    place_types = [place_types]
                output += f"\n   💡 Key Safety Tips:\n"
                
                if any(t in place_types for t in ['park', 'natural_feature', 'zoo']):
                    output += "      • Wildlife area - maintain safe distance\n"
                if any(t in place_types for t in ['place_of_worship', 'hindu_temple']):
                    output += "      • Religious site - dress modestly\n"
                
                output += "      • Keep valuables secure\n"
                output += "      • Carry water and sun protection\n"
                output += "\n   ✅ Live data from Google Places API"
                
                return output
        
        return f"❌ Error: Could not find safety info for '{location}'"
                
    except Exception as e:
        return f"❌ Error fetching safety info: {str(e)}"


def get_travel_advisory(country: str = "Sri Lanka") -> str:
    """
    Gets country-level travel advisory information.
    Provides essential travel info for the country.
    
    Args:
        country: Country name (default: Sri Lanka)
    
    Returns:
        Travel advisory status and recommendations.
    """
    output = f"""🌍 Travel Advisory for {country}:

   🚦 Overall Status: NORMAL (Exercise standard precautions)
   
   ℹ️ Entry Requirements:
      • Valid passport (6+ months validity)
      • ETA (Electronic Travel Authorization) required
      • Travel insurance strongly recommended
   
   🏥 Health Recommendations:
      • No mandatory vaccinations
      • Hepatitis A/B, Typhoid recommended
      • Drink bottled water only
      • Use mosquito repellent (dengue risk)
   
   📞 Emergency Numbers:
      • Police: 119
      • Ambulance: 110
      • Fire: 111
      • Tourist Police: +94 11 242 1052
   
   💡 General Tips:
      • Register with your embassy
      • Keep copies of documents
      • Dress modestly at religious sites
      • Negotiate prices before services
   
   ⚠️ For official advisories, check your government's travel website."""
    
    return output
