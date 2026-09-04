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
        self._mentions_cache: str | None = None

    async def get_chat_mentions(self) -> str:
        """
        Собрать @-упоминания участников чата.

        Bot API не отдаёт полный список участников — берём администраторов
        (для небольшой группы логирования это обычно все нужные люди).
        """
        if self._mentions_cache is not None:
            return self._mentions_cache

        url = f"{self.BASE_URL}/bot{self.token}/getChatAdministrators"
        mentions: list[str] = []
        try:
            response = await self.client.get(url, params={"chat_id": self.chat_id})
            response.raise_for_status()
            for item in response.json().get("result", []):
                user = item.get("user") or {}
                if user.get("is_bot"):
                    continue
                username = user.get("username")
                if username:
                    mentions.append(f"@{username}")
                else:
                    user_id = user.get("id")
                    name = user.get("first_name") or "user"
                    if user_id:
                        mentions.append(
                            f'<a href="tg://user?id={user_id}">{name}</a>'
                        )
        except httpx.HTTPError as e:
            logger.warning(f"Не удалось получить участников чата для упоминаний: {e}")

        self._mentions_cache = " ".join(mentions)
        return self._mentions_cache

    async def send_message(
        self, 
        text: str, 
        parse_mode: str = "HTML",
        mention_all: bool = True,
    ) -> bool:
        """
        Отправить сообщение в чат
        
        Args:
            text: Текст сообщения
            parse_mode: "HTML", "Markdown" или "MarkdownV2"
            mention_all: добавить в конце две пустые строки и @ участников
        
        Returns:
            True если успешно, False иначе
        """
        message = text.rstrip()
        if mention_all:
            mentions = await self.get_chat_mentions()
            message = f"{message}\n\n{mentions}" if mentions else f"{message}\n\n"

        url = f"{self.BASE_URL}/bot{self.token}/sendMessage"
        payload = {
            "chat_id": self.chat_id,
            "text": message,
            "parse_mode": parse_mode,
            "disable_web_page_preview": False,
        }
        
        try:
            response = await self.client.post(url, json=payload)
            response.raise_for_status()
            logger.info(f"Сообщение отправлено (длина: {len(message)} символов)")
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
