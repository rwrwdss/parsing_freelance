from .base import SourceHandler, LogEntry
from datetime import datetime, timezone
import logging

logger = logging.getLogger(__name__)


class WebhookHandler(SourceHandler):
    """Обработчик для HTTP webhook"""
    
    def __init__(self, name: str = "Webhook"):
        super().__init__(name)
    
    def process_webhook(
        self, 
        title: str, 
        content: str,
        url: str | None = None,
        tags: list[str] | None = None
    ) -> LogEntry:
        """
        Обработать входящий webhook
        
        Args:
            title: Заголовок
            content: Содержимое
            url: Ссылка (опционально)
            tags: Тэги (опционально)
        
        Returns:
            LogEntry для отправки в Telegram
        """
        return LogEntry(
            source=self.name,
            title=title,
            content=content,
            url=url,
            timestamp=datetime.now(tz=timezone.utc),
            tags=tags or [],
        )
    
    async def fetch(self) -> list[LogEntry]:
        """Webhook обработчик не использует fetch"""
        return []
