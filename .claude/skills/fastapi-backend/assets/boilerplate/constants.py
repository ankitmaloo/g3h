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

# Additional constants
DEFAULT_MODEL = "gpt-4-turbo"
DEFAULT_GEMINI_MODEL = "gemini-2.0-flash-exp"
MAX_TOKENS = 4096
TEMPERATURE = 0.7
