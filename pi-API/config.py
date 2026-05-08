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
    limit_x_pin: int = 16
    limit_y_pin: int = 18
    limit_z_pin: int = 4
    limit_sensor_active_state: int = 0
    limit_sensor_pull: str = "up"
    homing_max_steps: int = 20000
    homing_backoff_steps: int = 100
    homing_settle_seconds: float = 0.002


settings = Settings()
