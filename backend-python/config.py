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
    default_exposure: float = 100.0  # milliseconds (100ms)
    default_gain: float = 1.0
    image_save_path: str = "./captures"
    image_format: str = "jpg"
    image_quality: int = 95
    
    # Video Recording Configuration
    video_save_path: str = "./videos"
    video_format: str = "avi"
    video_default_duration: float = 10.0  # seconds
    video_default_playback_fps: float = 25.0
    video_default_decimation: int = 1
    
    # CORS Configuration
    allowed_origins: str = "http://localhost:3000,http://localhost:5173"
    
    @property
    def origins_list(self) -> List[str]:
        """Parse CORS origins from comma-separated string"""
        return [origin.strip() for origin in self.allowed_origins.split(",")]


# Global settings instance
settings = Settings()
