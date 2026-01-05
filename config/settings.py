"""
Configuration settings for Sri Lanka Travel Agent
"""
import os
from dotenv import load_dotenv

load_dotenv()


class Settings:
    """Application settings loaded from environment variables."""
    
    # API Keys
    OPENWEATHER_API_KEY: str = os.getenv("OPENWEATHER_API_KEY", "")
    GOOGLE_MAPS_API_KEY: str = os.getenv("GOOGLE_MAPS_API_KEY", "")
    GOOGLE_API_KEY: str = os.getenv("GOOGLE_API_KEY", "")
    GOOGLE_SEARCH_ENGINE_ID: str = os.getenv("GOOGLE_SEARCH_ENGINE_ID", "")
    
    # Application Settings
    APP_NAME: str = "sri_lanka_travel_agent"
    APP_VERSION: str = "2.0"
    DEBUG: bool = os.getenv("DEBUG", "false").lower() == "true"
    
    # Model Configuration
    DEFAULT_MODEL: str = os.getenv("DEFAULT_MODEL", "gemini-2.0-flash")
    
    # Server Configuration
    HOST: str = os.getenv("HOST", "0.0.0.0")
    PORT: int = int(os.getenv("PORT", "8000"))
    
    @classmethod
    def validate(cls) -> dict:
        """Validate that required API keys are configured."""
        missing = []
        
        if not cls.OPENWEATHER_API_KEY:
            missing.append("OPENWEATHER_API_KEY")
        if not cls.GOOGLE_MAPS_API_KEY:
            missing.append("GOOGLE_MAPS_API_KEY")
        if not cls.GOOGLE_API_KEY:
            missing.append("GOOGLE_API_KEY")
        
        return {
            "valid": len(missing) == 0,
            "missing": missing
        }


settings = Settings()
