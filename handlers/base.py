from abc import ABC, abstractmethod
from pydantic import BaseModel
from datetime import datetime


class LogEntry(BaseModel):
    """Базовая структура для логов"""
    
    source: str  # Откуда пришли (RSS, webhook, файл)
    title: str  # Заголовок / краткое описание
    content: str  # Полное содержимое
    url: str | None = None  # Ссылка на источник
    timestamp: datetime  # Когда обнаружено
    tags: list[str] = []  # Тэги для фильтрации
    
    def format_for_telegram(self) -> str:
        """Форматирование для Telegram"""
        lines = [
            f"📝 <b>{self.source}</b>",
            f"",
            f"<b>{self.title}</b>",
            f"",
            f"{self.content[:500]}{'...' if len(self.content) > 500 else ''}",
        ]
        
        if self.url:
            lines.append("")
            lines.append(f"🔗 <a href='{self.url}'>Открыть</a>")
        
        return "\n".join(lines)


class SourceHandler(ABC):
    """Базовый класс для обработчиков источников"""
    
    def __init__(self, name: str):
        self.name = name
    
    @abstractmethod
    async def fetch(self) -> list[LogEntry]:
        """
        Получить новые логи от источника
        
        Returns:
            Список новых логов
        """
        pass
