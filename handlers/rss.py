import feedparser
import html
import re
from datetime import datetime, timezone, timedelta
import logging
from .base import SourceHandler, LogEntry

logger = logging.getLogger(__name__)


class RSSHandler(SourceHandler):
    """Обработчик RSS лент"""
    
    def __init__(
        self,
        name: str,
        feed_url: str,
        max_items: int = 10,
        keywords: tuple[str, ...] | None = None,
    ):
        super().__init__(name)
        self.feed_url = feed_url
        self.max_items = max_items
        self.keywords = keywords or ()
        self.last_entries: set[str] = set()
    
    def _matches_keywords(self, title: str, content: str) -> bool:
        if not self.keywords:
            return True
        text = f"{title} {content}".lower()
        return any(keyword.lower() in text for keyword in self.keywords)
    
    async def fetch(self, since_minutes: int | None = None) -> list[LogEntry]:
        """
        Получить новые элементы из RSS.

        Args:
            since_minutes: если задано — только записи новее N минут (для serverless/cron)
        """
        try:
            feed = feedparser.parse(
                self.feed_url,
                agent="Mozilla/5.0 (compatible; CaseSearcherBot/1.0; +https://parsing-freelance.vercel.app)",
            )
            
            if feed.bozo:
                logger.warning(f"RSS парс ошибка {self.name}: {feed.bozo_exception}")
            
            cutoff = None
            if since_minutes is not None:
                cutoff = datetime.now(tz=timezone.utc) - timedelta(minutes=since_minutes)
            
            entries = []
            
            for item in feed.entries[: self.max_items]:
                item_id = item.get('id') or item.get('link', '')
                timestamp = self._parse_date(item)
                title = self._clean_text(item.get('title', 'Без заголовка'))
                content = self._extract_content(item)

                if not self._matches_keywords(title, content):
                    continue

                if cutoff and timestamp < cutoff:
                    continue

                if since_minutes is None and item_id in self.last_entries:
                    continue

                if since_minutes is None:
                    self.last_entries.add(item_id)
                    
                entry = LogEntry(
                    source=self.name,
                    title=title,
                    content=content,
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
    def _clean_text(text: str) -> str:
        text = re.sub(r'<[^>]+>', '', text)
        return html.unescape(text).strip()
    
    @staticmethod
    def _parse_date(item: dict) -> datetime:
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
        content = item.get('summary') or item.get('description', '')
        return RSSHandler._clean_text(content)
    
    @staticmethod
    def _extract_tags(item: dict) -> list[str]:
        tags = []
        
        if 'tags' in item:
            tags = [tag.get('term', '') for tag in item.tags]
        
        return [t for t in tags if t]
