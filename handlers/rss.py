import feedparser
from datetime import datetime, timezone
import logging
from .base import SourceHandler, LogEntry

logger = logging.getLogger(__name__)


class RSSHandler(SourceHandler):
    """Обработчик RSS лент"""
    
    def __init__(self, name: str, feed_url: str, max_items: int = 10):
        """
        Args:
            name: Имя источника (для логирования)
            feed_url: URL RSS ленты
            max_items: Максимум элементов за раз
        """
        super().__init__(name)
        self.feed_url = feed_url
        self.max_items = max_items
        self.last_entries = set()  # Для отслеживания новых
    
    async def fetch(self) -> list[LogEntry]:
        """Получить новые элементы из RSS"""
        try:
            feed = feedparser.parse(self.feed_url)
            
            if feed.bozo:
                logger.warning(f"RSS парс ошибка {self.name}: {feed.bozo_exception}")
            
            entries = []
            
            for item in feed.entries[:self.max_items]:
                # Генерируем уникальный ID элемента
                item_id = item.get('id') or item.get('link', '')
                
                # Если это новое, добавляем
                if item_id not in self.last_entries:
                    self.last_entries.add(item_id)
                    
                    # Парсим дату
                    timestamp = self._parse_date(item)
                    
                    entry = LogEntry(
                        source=self.name,
                        title=item.get('title', 'Без заголовка'),
                        content=self._extract_content(item),
                        url=item.get('link'),
                        timestamp=timestamp,
                        tags=self._extract_tags(item),
                    )
                    entries.append(entry)
            
            if entries:
                logger.info(f"RSS {self.name}: найдено {len(entries)} новых")
            
            return entries
        
        except Exception as e:
            logger.error(f"Ошибка парсинга RSS {self.name}: {e}")
            return []
    
    @staticmethod
    def _parse_date(item: dict) -> datetime:
        """Парсит дату из RSS элемента"""
        try:
            if 'published_parsed' in item:
                return datetime(*item.published_parsed[:6], tzinfo=timezone.utc)
            elif 'updated_parsed' in item:
                return datetime(*item.updated_parsed[:6], tzinfo=timezone.utc)
        except Exception:
            pass
        
        return datetime.now(tz=timezone.utc)
    
    @staticmethod
    def _extract_content(item: dict) -> str:
        """Извлекает основной контент элемента"""
        # Пробуем разные поля
        content = item.get('summary') or item.get('description', '')
        
        # Убираем HTML теги (простой способ)
        import re
        content = re.sub(r'<[^>]+>', '', content)
        
        return content.strip()
    
    @staticmethod
    def _extract_tags(item: dict) -> list[str]:
        """Извлекает тэги/категории"""
        tags = []
        
        if 'tags' in item:
            tags = [tag.get('term', '') for tag in item.tags]
        
        return [t for t in tags if t]
