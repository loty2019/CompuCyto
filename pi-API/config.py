"""
Configuration module for Pi-API
"""
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables"""
    
    model_config = SettingsConfigDict(env_file='.env', env_file_encoding='utf-8')
    
    host: str = "0.0.0.0"
    port: int = 8000
    jwt_secret: str = ""
    dht11_pin: int = 24


settings = Settings()
