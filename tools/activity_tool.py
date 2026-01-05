"""
Activity Tool - Searches for attractions using Google Places API ONLY
No mock/fallback data - requires API key
"""
import os
from dotenv import load_dotenv
import googlemaps

load_dotenv()


def get_activities(interest: str, location: str = "Sri Lanka") -> str:
    """
    Searches for tourist activities and attractions using Google Places API.
    Returns real place data with ratings and addresses.
    
    Args:
        interest: Type of activity (e.g., "heritage", "beach", "wildlife", "temple")
        location: Location to search near (default: "Sri Lanka")
    
    Returns:
        List of real places with ratings from Google Places.
    """
    api_key = os.getenv("GOOGLE_MAPS_API_KEY")
    
    if not api_key:
        return "❌ Error: GOOGLE_MAPS_API_KEY not configured in .env file"

    try:
        gmaps = googlemaps.Client(key=api_key)
        
        # Build search query
        query = f"{interest} attractions in {location}"
        
        # Use Places Text Search API
        places_result = gmaps.places(query=query)
        
        if places_result['status'] == 'OK':
            results = places_result['results'][:7]  # Top 7 results
            
            if not results:
                return f"❌ No {interest} activities found in {location}"
            
            output = f"🎯 {interest.title()} Activities in {location}:\n"
            
            for i, place in enumerate(results, 1):
                name = place.get('name', 'Unknown')
                rating = place.get('rating', 'N/A')
                user_ratings = place.get('user_ratings_total', 0)
                address = place.get('formatted_address', place.get('vicinity', 'Address not available'))
                
                # Get place types
                types = place.get('types', [])
                type_str = ', '.join([t.replace('_', ' ').title() for t in types[:2]])
                
                # Check if open now
                opening_hours = place.get('opening_hours', {})
                is_open = opening_hours.get('open_now')
                open_status = "🟢 Open" if is_open else "🔴 Closed" if is_open is False else ""
                
                output += f"\n   {i}. {name}\n"
                output += f"      ⭐ Rating: {rating}/5 ({user_ratings} reviews)\n"
                output += f"      📍 {address}\n"
                if type_str:
                    output += f"      🏷️ {type_str}\n"
                if open_status:
                    output += f"      {open_status}\n"
            
            output += "\n   ✅ Live data from Google Places API"
            return output
            
        elif places_result['status'] == 'ZERO_RESULTS':
            return f"❌ No {interest} activities found in {location}"
        else:
            return f"❌ API Error: {places_result['status']}"
            
    except googlemaps.exceptions.ApiError as e:
        return f"❌ Google Places API Error: {str(e)}"
    except Exception as e:
        return f"❌ Error: {str(e)}"


def get_place_details(place_name: str, location: str = "Sri Lanka") -> str:
    """
    Gets detailed information about a specific place.
    
    Args:
        place_name: Name of the place (e.g., "Sigiriya Rock Fortress")
        location: Location context (default: "Sri Lanka")
    
    Returns:
        Detailed place information including hours, phone, website.
    """
    api_key = os.getenv("GOOGLE_MAPS_API_KEY")
    
    if not api_key:
        return "❌ Error: GOOGLE_MAPS_API_KEY not configured in .env file"

    try:
        gmaps = googlemaps.Client(key=api_key)
        
        # First find the place
        places_result = gmaps.places(query=f"{place_name}, {location}")
        
        if places_result['status'] == 'OK' and places_result['results']:
            place_id = places_result['results'][0]['place_id']
            
            # Get detailed info
            details = gmaps.place(place_id=place_id, fields=[
                'name', 'formatted_address', 'formatted_phone_number',
                'rating', 'user_ratings_total', 'opening_hours',
                'website', 'reviews', 'price_level', 'types'
            ])
            
            if details['status'] == 'OK':
                result = details['result']
                
                output = f"📍 {result.get('name', place_name)}\n"
                output += f"   📫 Address: {result.get('formatted_address', 'N/A')}\n"
                
                if result.get('rating'):
                    output += f"   ⭐ Rating: {result['rating']}/5 ({result.get('user_ratings_total', 0)} reviews)\n"
                
                if result.get('formatted_phone_number'):
                    output += f"   📞 Phone: {result['formatted_phone_number']}\n"
                
                if result.get('website'):
                    output += f"   🌐 Website: {result['website']}\n"
                
                # Opening hours
                hours = result.get('opening_hours', {})
                if hours.get('weekday_text'):
                    output += f"   🕐 Hours:\n"
                    for day in hours['weekday_text'][:3]:  # First 3 days
                        output += f"      {day}\n"
                
                # Price level
                price = result.get('price_level')
                if price is not None:
                    price_str = '$' * (price + 1)
                    output += f"   💰 Price Level: {price_str}\n"
                
                output += "\n   ✅ Live data from Google Places API"
                return output
        
        return f"❌ Place '{place_name}' not found"
            
    except Exception as e:
        return f"❌ Error: {str(e)}"
