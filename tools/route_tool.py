"""
Route Tool - Calculates distances, travel times, and directions using Google Maps API
Uses ONLY real API data - no mock/fallback data
"""
import os
from dotenv import load_dotenv
import googlemaps

load_dotenv()


def get_route(origin: str, destination: str, mode: str = "driving") -> str:
    """
    Calculates travel distance and duration between two locations in Sri Lanka.
    Uses Google Maps Distance Matrix API for live data.
    
    Args:
        origin: Starting location (e.g., "Colombo")
        destination: End location (e.g., "Kandy")
        mode: Travel mode - "driving", "walking", "transit", "bicycling" (default: "driving")
    
    Returns:
        Route information including distance and estimated duration.
    """
    api_key = os.getenv("GOOGLE_MAPS_API_KEY")
    
    if not api_key:
        return "❌ Error: GOOGLE_MAPS_API_KEY not configured in .env file"

    try:
        gmaps = googlemaps.Client(key=api_key)
        
        # Use Distance Matrix API for distance and duration
        matrix = gmaps.distance_matrix(
            origins=f"{origin}, Sri Lanka",
            destinations=f"{destination}, Sri Lanka",
            mode=mode
        )
        
        if matrix['status'] == 'OK':
            element = matrix['rows'][0]['elements'][0]
            if element['status'] == 'OK':
                distance = element['distance']['text']
                duration = element['duration']['text']
                return f"🗺️ Route: {origin} → {destination} ({mode})\n   📏 Distance: {distance}\n   ⏱️ Duration: {duration}\n   ✅ Live data from Google Maps"
            else:
                return f"❌ Route not found: {element['status']} - Check location names"
        return f"❌ API Error: {matrix['status']}"
        
    except googlemaps.exceptions.ApiError as e:
        return f"❌ Google Maps API Error: {str(e)}"
    except Exception as e:
        return f"❌ Error: {str(e)}"


def get_directions(origin: str, destination: str) -> str:
    """
    Gets detailed step-by-step driving directions between two locations.
    Uses Google Maps Directions API for live data.
    
    Args:
        origin: Starting location (e.g., "Colombo")
        destination: End location (e.g., "Kandy")
    
    Returns:
        Step-by-step directions with turn-by-turn instructions.
    """
    api_key = os.getenv("GOOGLE_MAPS_API_KEY")
    
    if not api_key:
        return "❌ Error: GOOGLE_MAPS_API_KEY not configured in .env file"

    try:
        gmaps = googlemaps.Client(key=api_key)
        
        # Use Directions API for step-by-step navigation
        directions = gmaps.directions(
            origin=f"{origin}, Sri Lanka",
            destination=f"{destination}, Sri Lanka",
            mode="driving"
        )
        
        if directions:
            route = directions[0]
            leg = route['legs'][0]
            
            result = f"📍 Directions: {origin} → {destination}\n"
            result += f"   📏 Total Distance: {leg['distance']['text']}\n"
            result += f"   ⏱️ Total Duration: {leg['duration']['text']}\n"
            result += f"   📍 Start: {leg['start_address']}\n"
            result += f"   🏁 End: {leg['end_address']}\n"
            result += f"\n🚗 Step-by-step ({len(leg['steps'])} steps):\n"
            
            # Show ALL steps
            for i, step in enumerate(leg['steps'], 1):
                # Clean HTML tags from instructions
                instruction = step['html_instructions']
                instruction = instruction.replace('<b>', '').replace('</b>', '')
                instruction = instruction.replace('<div style="font-size:0.9em">', ' - ')
                instruction = instruction.replace('</div>', '')
                instruction = instruction.replace('<wbr/>', '')
                
                distance = step['distance']['text']
                duration = step.get('duration', {}).get('text', '')
                
                if duration:
                    result += f"   {i}. {instruction} ({distance}, {duration})\n"
                else:
                    result += f"   {i}. {instruction} ({distance})\n"
            
            result += f"\n   ✅ Live directions from Google Maps"
            return result
        else:
            return f"❌ No route found from {origin} to {destination}"
            
    except googlemaps.exceptions.ApiError as e:
        return f"❌ Google Maps API Error: {str(e)}"
    except Exception as e:
        return f"❌ Error: {str(e)}"


def get_travel_options(origin: str, destination: str) -> str:
    """
    Compares different travel modes (driving, transit, walking) for a route.
    
    Args:
        origin: Starting location
        destination: End location
    
    Returns:
        Comparison of travel times and distances for different modes.
    """
    api_key = os.getenv("GOOGLE_MAPS_API_KEY")
    
    if not api_key:
        return "❌ Error: GOOGLE_MAPS_API_KEY not configured in .env file"

    try:
        gmaps = googlemaps.Client(key=api_key)
        
        modes = ["driving", "transit", "walking"]
        results = []
        
        for mode in modes:
            try:
                matrix = gmaps.distance_matrix(
                    origins=f"{origin}, Sri Lanka",
                    destinations=f"{destination}, Sri Lanka",
                    mode=mode
                )
                
                if matrix['status'] == 'OK':
                    element = matrix['rows'][0]['elements'][0]
                    if element['status'] == 'OK':
                        distance = element['distance']['text']
                        duration = element['duration']['text']
                        results.append(f"   🚗 {mode.capitalize()}: {distance}, {duration}")
                    else:
                        results.append(f"   ❌ {mode.capitalize()}: Not available")
            except:
                results.append(f"   ❌ {mode.capitalize()}: Error")
        
        output = f"🗺️ Travel Options: {origin} → {destination}\n"
        output += "\n".join(results)
        output += "\n   ✅ Live data from Google Maps"
        return output
        
    except Exception as e:
        return f"❌ Error: {str(e)}"
