"""
Weather Tool - Fetches REAL weather data from OpenWeatherMap API
NO mock/fallback data - returns actual API errors if issues occur
"""
import requests
import os
from dotenv import load_dotenv

load_dotenv()


def get_weather(location: str) -> str:
    """
    Retrieves current weather data for a specific location in Sri Lanka.
    Uses OpenWeatherMap API for REAL data only.
    
    Args:
        location: The city or location name in Sri Lanka (e.g., "Colombo", "Kandy")
    
    Returns:
        Weather description including temperature and conditions.
    """
    api_key = os.getenv("OPENWEATHER_API_KEY")
    
    if not api_key:
        return "❌ Error: OPENWEATHER_API_KEY not configured in .env file"

    try:
        url = f"https://api.openweathermap.org/data/2.5/weather?q={location},LK&appid={api_key}&units=metric"
        response = requests.get(url, timeout=10)
        data = response.json()
        
        if response.status_code == 200:
            weather_desc = data['weather'][0]['description']
            temp = data['main']['temp']
            feels_like = data['main']['feels_like']
            humidity = data['main']['humidity']
            wind_speed = data['wind']['speed']
            
            return f"""🌤️ Weather in {location}:
   📝 Conditions: {weather_desc.title()}
   🌡️ Temperature: {temp}°C (Feels like {feels_like}°C)
   💧 Humidity: {humidity}%
   💨 Wind: {wind_speed} m/s
   ✅ Live data from OpenWeatherMap"""
        
        elif response.status_code == 401:
            return "❌ Error: Invalid OpenWeatherMap API key"
        elif response.status_code == 404:
            return f"❌ Error: Location '{location}' not found in Sri Lanka"
        else:
            return f"❌ API Error ({response.status_code}): {data.get('message', 'Unknown error')}"
            
    except requests.exceptions.Timeout:
        return f"❌ Error: Request timed out for {location}"
    except requests.exceptions.ConnectionError:
        return "❌ Error: Could not connect to OpenWeatherMap API"
    except Exception as e:
        return f"❌ Error fetching weather: {str(e)}"


def get_weather_forecast(location: str, days: int = 5) -> str:
    """
    Gets weather forecast for upcoming days.
    Uses OpenWeatherMap 5-day forecast API for REAL data only.
    
    Args:
        location: The city name in Sri Lanka
        days: Number of days to forecast (max 5)
    
    Returns:
        Multi-day weather forecast.
    """
    api_key = os.getenv("OPENWEATHER_API_KEY")
    
    if not api_key:
        return "❌ Error: OPENWEATHER_API_KEY not configured in .env file"

    try:
        url = f"https://api.openweathermap.org/data/2.5/forecast?q={location},LK&appid={api_key}&units=metric"
        response = requests.get(url, timeout=10)
        data = response.json()
        
        if response.status_code == 200:
            result = f"📅 {days}-Day Forecast for {location}:\n"
            
            # Get one forecast per day (every 8th item = 24 hours)
            forecasts = data['list']
            daily_forecasts = forecasts[::8][:days]
            
            for forecast in daily_forecasts:
                date = forecast['dt_txt'].split(' ')[0]
                temp = forecast['main']['temp']
                desc = forecast['weather'][0]['description']
                humidity = forecast['main']['humidity']
                
                result += f"\n   📆 {date}:\n"
                result += f"      🌡️ {temp}°C | {desc.title()}\n"
                result += f"      💧 Humidity: {humidity}%\n"
            
            result += "\n   ✅ Live forecast from OpenWeatherMap"
            return result
        
        elif response.status_code == 401:
            return "❌ Error: Invalid OpenWeatherMap API key"
        elif response.status_code == 404:
            return f"❌ Error: Location '{location}' not found"
        else:
            return f"❌ API Error ({response.status_code}): {data.get('message', 'Unknown error')}"
            
    except requests.exceptions.Timeout:
        return f"❌ Error: Forecast request timed out for {location}"
    except requests.exceptions.ConnectionError:
        return "❌ Error: Could not connect to OpenWeatherMap API"
    except Exception as e:
        return f"❌ Error fetching forecast: {str(e)}"
