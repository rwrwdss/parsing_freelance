import httpx
from config import settings
import logging

logger = logging.getLogger(__name__)


class TelegramService:
    """Сервис для отправки сообщений в Telegram"""
    
    BASE_URL = "https://api.telegram.org"
    
    def __init__(self, token: str, chat_id: str):
        self.token = token
        self.chat_id = chat_id
        self.client = httpx.AsyncClient(timeout=10.0)
    
    async def send_message(
        self, 
        text: str, 
        parse_mode: str = "HTML"
    ) -> bool:
        """
        Отправить сообщение в чат
        
        Args:
            text: Текст сообщения
            parse_mode: "HTML", "Markdown" или "MarkdownV2"
        
        Returns:
            True если успешно, False иначе
        """
        url = f"{self.BASE_URL}/bot{self.token}/sendMessage"
        payload = {
            "chat_id": self.chat_id,
            "text": text,
            "parse_mode": parse_mode,
            "disable_web_page_preview": False,
        }
        
        try:
            response = await self.client.post(url, json=payload)
            response.raise_for_status()
            logger.info(f"Сообщение отправлено (длина: {len(text)} символов)")
            return True
        except httpx.HTTPError as e:
            logger.error(f"Ошибка отправки в Telegram: {e}")
            return False
    
    async def close(self):
        """Закрыть соединение"""
        await self.client.aclose()


# Глобальный инстанс
telegram = TelegramService(
    token=settings.telegram_bot_token,
    chat_id=settings.telegram_chat_id
)
