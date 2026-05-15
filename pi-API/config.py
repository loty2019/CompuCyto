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
    dht11_read_attempts: int = 3
    dht11_retry_seconds: float = 1.2
    limit_x_pin: int = 16
    limit_y_pin: int = 18
    limit_z_pin: int = 4
    limit_sensor_active_state: int = 0
    limit_sensor_pull: str = "up"
    step_pulse_seconds: float = 0.0010
    step_low_seconds: float = 0.0010
    direction_settle_seconds: float = 0.005
    limit_poll_seconds: float = 0.01
    limit_debounce_seconds: float = 0.03
    homing_fast_step_seconds: float = 0.0015
    homing_slow_step_seconds: float = 0.0025
    homing_max_steps: int = 50000
    homing_backoff_steps: int = 300
    max_x_position: int = 8500
    max_y_position: int = 100000
    max_z_position: int = 10000


settings = Settings()
