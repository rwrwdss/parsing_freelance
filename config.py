from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Глобальные настройки приложения"""

    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=False,
    )

    # Telegram
    telegram_bot_token: str
    telegram_chat_id: str

    # RSS
    rss_check_interval: int = 300  # секунды

    # Debug
    debug: bool = False

    # Cron (Vercel / внешний cron-job.org)
    cron_secret: str = ""

    @field_validator("rss_check_interval", mode="before")
    @classmethod
    def empty_int_uses_default(cls, value):
        if value == "" or value is None:
            return 300
        return value

    @field_validator("debug", mode="before")
    @classmethod
    def empty_bool_uses_default(cls, value):
        if value == "" or value is None:
            return False
        return value


settings = Settings()
