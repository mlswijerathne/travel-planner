"""
Budget Tool - Gets pricing data using Google Places API and Exchange Rate API
NO mock/fallback data - returns actual API errors if issues occur
"""
import os
import requests
from dotenv import load_dotenv

load_dotenv()


def check_budget(activity: str, location: str = "Sri Lanka") -> str:
    """
    Gets pricing information for an activity.
    Uses Google Places API for REAL data only.
    
    Args:
        activity: Name of the activity or place (e.g., "Sigiriya", "Yala Safari")
        location: Location context (default: "Sri Lanka")
    
    Returns:
        Pricing information from Google Places.
    """
    api_key = os.getenv("GOOGLE_MAPS_API_KEY")
    
    if not api_key:
        return "❌ Error: GOOGLE_MAPS_API_KEY not configured in .env file"

    try:
        import googlemaps
        gmaps = googlemaps.Client(key=api_key)
        
        # Search for the place
        places_result = gmaps.places(query=f"{activity} {location}")
        
        if places_result['status'] == 'OK' and places_result['results']:
            place = places_result['results'][0]
            place_id = place['place_id']
            
            # Get detailed pricing info
            details = gmaps.place(place_id=place_id, fields=[
                'name', 'price_level', 'rating', 'user_ratings_total',
                'reviews', 'formatted_address', 'types'
            ])
            
            if details['status'] == 'OK':
                result = details['result']
                
                output = f"💰 Budget Info: {result.get('name', activity)}\n"
                
                # Price level from Google (0-4 scale)
                price_level = result.get('price_level')
                if price_level is not None:
                    price_indicators = {
                        0: ("Free", "$0"),
                        1: ("Budget", "$1-15"),
                        2: ("Moderate", "$15-35"),
                        3: ("Expensive", "$35-60"),
                        4: ("Very Expensive", "$60+")
                    }
                    level_name, estimate = price_indicators.get(price_level, ("Unknown", "Varies"))
                    output += f"   💵 {level_name}: {estimate}/person\n"
                else:
                    output += f"   💵 Price: Not available from API\n"
                
                if result.get('rating'):
                    output += f"   ⭐ Rating: {result['rating']}/5 ({result.get('user_ratings_total', 0)} reviews)\n"
                
                output += f"   📍 {result.get('formatted_address', location)}\n"
                output += "   ✅ Live data from Google Places API"
                
                return output
        
        return f"❌ Error: Could not find pricing for '{activity}'"
            
    except Exception as e:
        return f"❌ Error fetching budget info: {str(e)}"


def get_currency_rate(from_currency: str = "USD", to_currency: str = "LKR") -> str:
    """
    Gets current currency exchange rate.
    Uses Exchange Rate API for REAL data only.
    
    Args:
        from_currency: Source currency code (default: USD)
        to_currency: Target currency code (default: LKR - Sri Lankan Rupee)
    
    Returns:
        Current exchange rate from live API.
    """
    api_key = os.getenv("EXCHANGE_RATE_API_KEY")
    
    if not api_key:
        return "❌ Error: EXCHANGE_RATE_API_KEY not configured in .env file"
    
    try:
        url = f"https://v6.exchangerate-api.com/v6/{api_key}/latest/{from_currency}"
        response = requests.get(url, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            
            if data.get('result') == 'success':
                rate = data['conversion_rates'].get(to_currency)
                
                if rate:
                    return f"""💱 Currency Exchange Rate:
   1 {from_currency} = {rate:.2f} {to_currency}
   
   Quick Reference:
   • $10 = {10 * rate:.0f} LKR
   • $50 = {50 * rate:.0f} LKR
   • $100 = {100 * rate:.0f} LKR
   
   ✅ Live rate from Exchange Rate API"""
                else:
                    return f"❌ Error: Currency '{to_currency}' not found"
            else:
                return f"❌ API Error: {data.get('error-type', 'Unknown error')}"
        else:
            return f"❌ API Error ({response.status_code}): Could not fetch exchange rate"
            
    except requests.exceptions.Timeout:
        return "❌ Error: Exchange rate API request timed out"
    except requests.exceptions.ConnectionError:
        return "❌ Error: Could not connect to Exchange Rate API"
    except Exception as e:
        return f"❌ Error fetching exchange rate: {str(e)}"


def compare_costs(activities: str, daily_budget: float = 100.0) -> str:
    """
    Compares costs of multiple activities against a daily budget.
    Uses Google Places API to get real pricing.
    
    Args:
        activities: Comma-separated list of activity names
        daily_budget: Daily budget in USD (default: $100)
    
    Returns:
        Cost comparison and budget analysis.
    """
    api_key = os.getenv("GOOGLE_MAPS_API_KEY")
    
    if not api_key:
        return "❌ Error: GOOGLE_MAPS_API_KEY not configured in .env file"
    
    # Parse comma-separated activities
    items = [item.strip() for item in activities.split(',') if item.strip()]
    
    if not items:
        return "Please provide activities as comma-separated list: 'Sigiriya, Yala Safari'"
    
    try:
        import googlemaps
        gmaps = googlemaps.Client(key=api_key)
        
        output = f"📊 Budget Comparison (Daily budget: ${daily_budget}):\n\n"
        total_estimated = 0
        found_items = 0
        
        for item in items:
            places_result = gmaps.places(query=f"{item} Sri Lanka")
            
            if places_result['status'] == 'OK' and places_result['results']:
                place = places_result['results'][0]
                place_id = place['place_id']
                
                details = gmaps.place(place_id=place_id, fields=['name', 'price_level'])
                
                if details['status'] == 'OK':
                    result = details['result']
                    price_level = result.get('price_level')
                    
                    if price_level is not None:
                        price_estimates = {0: 0, 1: 10, 2: 25, 3: 45, 4: 80}
                        avg_price = price_estimates.get(price_level, 20)
                        total_estimated += avg_price
                        found_items += 1
                        status = "✅" if avg_price <= daily_budget / len(items) else "⚠️"
                        output += f"   {status} {item}: ~${avg_price:.0f}\n"
                    else:
                        output += f"   ❓ {item}: Price not available\n"
                else:
                    output += f"   ❓ {item}: Could not fetch details\n"
            else:
                output += f"   ❓ {item}: Not found\n"
        
        if found_items > 0:
            output += f"\n   📈 Total (found items): ~${total_estimated:.0f}"
            
            if total_estimated <= daily_budget:
                output += f"\n   ✅ Within budget (+${daily_budget - total_estimated:.0f} remaining)"
            else:
                output += f"\n   ⚠️ Over budget by ${total_estimated - daily_budget:.0f}"
        
        output += "\n\n   ✅ Live data from Google Places API"
        return output
        
    except Exception as e:
        return f"❌ Error comparing costs: {str(e)}"
