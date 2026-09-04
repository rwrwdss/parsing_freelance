import httpx
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from telegram_service import TelegramService


class TestTelegramService:
    """Тесты Telegram сервиса"""
    
    @pytest.mark.asyncio
    async def test_send_message_success(self):
        """Проверяем успешную отправку сообщения"""
        service = TelegramService(token="test_token", chat_id="123")
        
        with (
            patch.object(service, "get_chat_mentions", new_callable=AsyncMock) as mock_mentions,
            patch.object(service.client, "post", new_callable=AsyncMock) as mock_post,
        ):
            mock_mentions.return_value = "@alice @bob"
            mock_response = MagicMock()
            mock_response.raise_for_status = MagicMock()
            mock_post.return_value = mock_response
            
            result = await service.send_message("Test message")
            
            assert result is True
            mock_post.assert_called_once()
            sent_text = mock_post.call_args.kwargs["json"]["text"]
            assert sent_text == "Test message\n\n@alice @bob"

    @pytest.mark.asyncio
    async def test_send_message_failure(self):
        """Проверяем обработку ошибок отправки"""
        service = TelegramService(token="test_token", chat_id="123")
        
        with (
            patch.object(service, "get_chat_mentions", new_callable=AsyncMock) as mock_mentions,
            patch.object(service.client, "post", new_callable=AsyncMock) as mock_post,
        ):
            mock_mentions.return_value = ""
            mock_post.side_effect = httpx.ConnectError(
                "Network error",
                request=httpx.Request("POST", "https://api.telegram.org/bot/sendMessage"),
            )
            
            result = await service.send_message("Test message")
            
            assert result is False
