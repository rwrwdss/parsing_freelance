from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """Глобальные настройки приложения"""
    
    # Telegram
    telegram_bot_token: str
    telegram_chat_id: str
    
    # RSS
    rss_check_interval: int = 300  # секунды
    
    # Debug
    debug: bool = False
    
    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings()
