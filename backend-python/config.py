"""
Configuration module for FastAPI Camera Service
Loads settings from environment variables with sensible defaults
"""
from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    """Application settings loaded from environment variables"""
    
    # Server Configuration
    host: str = "0.0.0.0"
    port: int = 8001
    debug: bool = True
    
    # Camera Configuration
    camera_serial_number: str = ""  # Empty means use first available camera
    default_exposure: float = 100.0  # milliseconds
    default_gain: float = 1.0
    image_save_path: str = "./captures"
    image_format: str = "jpg"
    image_quality: int = 95
    
    # CORS Configuration
    allowed_origins: str = "http://localhost:3000,http://localhost:5173"
    
    @property
    def origins_list(self) -> List[str]:
        """Parse CORS origins from comma-separated string"""
        return [origin.strip() for origin in self.allowed_origins.split(",")]
    
    class Config:
        env_file = ".env"
        case_sensitive = False


# Global settings instance
settings = Settings()
