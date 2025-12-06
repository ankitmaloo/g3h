"""
Constants for the application
"""

import os
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings from environment variables"""
    
    # API Keys
    openai_api_key: str = ""
    google_api_key: str = ""
    
    # Firebase
    firebase_project_id: str = ""
    firebase_private_key_id: str = ""
    firebase_private_key: str = ""
    firebase_client_email: str = ""
    firebase_client_id: str = ""
    
    # Application
    debug: bool = False
    port: int = 8000
    host: str = "0.0.0.0"
    
    # CORS
    allowed_origins: str = "*"
    
    class Config:
        env_file = ".env"
        case_sensitive = False


# Initialize settings
settings = Settings()

# Additional constants - Latest Gemini Models (2025)
DEFAULT_GEMINI_MODEL = "gemini-2.5-flash"  # Best price-performance
GEMINI_3_PRO = "gemini-3-pro-preview"  # Best multimodal understanding
GEMINI_25_PRO = "gemini-2.5-pro"  # Best for complex reasoning
GEMINI_25_FLASH = "gemini-2.5-flash"  # Best for large-scale processing
GEMINI_25_FLASH_LITE = "gemini-2.5-flash-lite"  # Fastest, most cost-efficient

MAX_TOKENS = 8192
TEMPERATURE = 0.7
