import pytest
from datetime import datetime, timezone
from handlers import RSSHandler, WebhookHandler, LogEntry


class TestRSSHandler:
    """Тесты RSS обработчика"""
    
    @pytest.mark.asyncio
    async def test_rss_fetch_freelance(self):
        """Проверяем парсинг реальной ленты Freelance.ru"""
        handler = RSSHandler(
            name="Freelance Test",
            feed_url="https://www.fl.ru/rss/?category=5",
            max_items=5,
        )
        
        entries = await handler.fetch()
        
        # Проверяем, что получили хоть что-то
        assert isinstance(entries, list)
        
        # Если ленты не пусты
        if entries:
            entry = entries[0]
            assert isinstance(entry, LogEntry)
            assert entry.source == "Freelance Test"
            assert entry.title
            assert entry.content
            assert entry.url
            assert isinstance(entry.timestamp, datetime)
    
    @pytest.mark.asyncio
    async def test_rss_duplicate_prevention(self):
        """Проверяем что не добавляются дубликаты"""
        handler = RSSHandler(
            name="Duplicate Test",
            feed_url="https://www.fl.ru/rss/?category=5",
            max_items=10,
        )
        
        # Первый запрос
        entries1 = await handler.fetch()
        count1 = len(entries1)
        
        # Второй запрос - должны быть только новые
        entries2 = await handler.fetch()
        
        # Если ленты активны, дубликатов быть не должно
        seen_ids = set()
        for entry in entries1 + entries2:
            # Используем URL как уникальный ID
            assert entry.url not in seen_ids, "Найден дубликат!"
            seen_ids.add(entry.url)


class TestWebhookHandler:
    """Тесты Webhook обработчика"""
    
    def test_webhook_process(self):
        """Проверяем обработку webhook данных"""
        handler = WebhookHandler("Test Webhook")
        
        log_entry = handler.process_webhook(
            title="Test",
            content="Test content",
            url="https://example.com",
            tags=["test", "example"]
        )
        
        assert log_entry.source == "Test Webhook"
        assert log_entry.title == "Test"
        assert log_entry.content == "Test content"
        assert log_entry.url == "https://example.com"
        assert log_entry.tags == ["test", "example"]
        assert isinstance(log_entry.timestamp, datetime)
    
    def test_webhook_format_telegram(self):
        """Проверяем форматирование для Telegram"""
        handler = WebhookHandler()
        log_entry = handler.process_webhook(
            title="Test Title",
            content="Test content here",
            url="https://example.com",
        )
        
        formatted = log_entry.format_for_telegram()
        
        assert "Test Title" in formatted
        assert "Test content" in formatted
        assert "https://example.com" in formatted
        assert "<b>" in formatted  # HTML форматирование


class TestLogEntry:
    """Тесты структуры LogEntry"""
    
    def test_log_entry_creation(self):
        """Проверяем создание LogEntry"""
        now = datetime.now(tz=timezone.utc)
        entry = LogEntry(
            source="test",
            title="Test",
            content="Content",
            timestamp=now,
        )
        
        assert entry.source == "test"
        assert entry.title == "Test"
        assert entry.url is None
        assert entry.tags == []
    
    def test_log_entry_format_without_url(self):
        """Проверяем форматирование без URL"""
        entry = LogEntry(
            source="test",
            title="Title",
            content="Content here",
            timestamp=datetime.now(tz=timezone.utc),
        )
        
        formatted = entry.format_for_telegram()
        assert "Title" in formatted
        assert "Content" in formatted
        assert "Открыть" not in formatted  # Нет ссылки
