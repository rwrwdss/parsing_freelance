import asyncio
import logging
import os
from fastapi import FastAPI, HTTPException, Header
from pydantic import BaseModel
from contextlib import asynccontextmanager

from config import settings
from telegram_service import telegram
from handlers import RSSHandler, WebhookHandler, LogEntry
from rss_sources import RSS_FEEDS

IS_VERCEL = os.getenv("VERCEL") == "1"

# Конфигурация логирования
logging.basicConfig(
    level=logging.DEBUG if settings.debug else logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


# Хранилище обработчиков
handlers = []
background_task = None


async def initialize_handlers():
    """Инициализирует все обработчики источников"""
    global handlers
    handlers.clear()

    for feed in RSS_FEEDS:
        handlers.append(
            RSSHandler(
                name=feed.name,
                feed_url=feed.feed_url,
                max_items=feed.max_items,
            )
        )

    logger.info(f"Инициализировано {len(handlers)} обработчиков")


async def fetch_and_send_rss(since_minutes: int | None = None) -> dict:
    """Проверяет RSS и отправляет новые записи в Telegram"""
    if not handlers:
        await initialize_handlers()

    sent = 0
    errors = 0
    checked = len(handlers)

    for handler in handlers:
        try:
            logs = await handler.fetch(since_minutes=since_minutes)
            for log in logs:
                message = log.format_for_telegram()
                if await telegram.send_message(message):
                    sent += 1
                else:
                    errors += 1
        except Exception as e:
            logger.error(f"Ошибка обработчика {handler.name}: {e}")
            errors += 1

    return {"checked": checked, "sent": sent, "errors": errors}


async def background_fetch_loop():
    """Фоновый цикл для проверки новых логов"""
    logger.info("Запущен фоновый цикл проверки логов")
    
    while True:
        try:
            for handler in handlers:
                try:
                    logs = await handler.fetch()
                    for log in logs:
                        message = log.format_for_telegram()
                        await telegram.send_message(message)
                
                except Exception as e:
                    logger.error(f"Ошибка обработчика {handler.name}: {e}")
            
            # Ждём перед следующей проверкой
            await asyncio.sleep(settings.rss_check_interval)
        
        except asyncio.CancelledError:
            logger.info("Фоновый цикл остановлен")
            break
        except Exception as e:
            logger.error(f"Неожиданная ошибка в цикле: {e}")
            await asyncio.sleep(60)  # Переждём и продолжим


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Управление жизненным циклом приложения"""
    global background_task
    
    # Startup
    await initialize_handlers()
    if not IS_VERCEL:
        background_task = asyncio.create_task(background_fetch_loop())
        logger.info("Приложение запущено (фоновый RSS-цикл активен)")
    else:
        logger.info("Приложение запущено на Vercel (фоновый цикл отключён)")
    
    yield
    
    # Shutdown
    if background_task:
        background_task.cancel()
        try:
            await background_task
        except asyncio.CancelledError:
            pass
    
    await telegram.close()
    logger.info("Приложение остановлено")


# Создаём FastAPI приложение
app = FastAPI(
    title="Telegram Logs Bot",
    description="Бот для отправки логов из разных источников в Telegram",
    version="1.0.0",
    lifespan=lifespan,
)


# Модели для webhook
class WebhookPayload(BaseModel):
    title: str
    content: str
    url: str | None = None
    tags: list[str] | None = None


# API Endpoints
@app.get("/")
async def root():
    """Корневая страница"""
    return {
        "service": "Telegram Logs Bot",
        "docs": "/docs",
        "health": "/health",
        "webhook": "/webhook",
        "cron": "/cron/rss",
    }


def _verify_cron_auth(authorization: str | None) -> None:
    """Проверка секрета для cron endpoint"""
    secret = settings.cron_secret or os.getenv("CRON_SECRET", "")
    if not secret:
        return
    expected = f"Bearer {secret}"
    if authorization != expected:
        raise HTTPException(status_code=401, detail="Unauthorized")


@app.get("/cron/rss")
async def cron_rss(authorization: str | None = Header(default=None)):
    """
    Cron endpoint: проверяет RSS и шлёт новые заказы в Telegram.
    На Vercel вызывается по расписанию; можно дергать вручную или через cron-job.org.
    """
    _verify_cron_auth(authorization)

    # Окно чуть шире интервала, чтобы не пропустить заказы между запусками
    since_minutes = max(settings.rss_check_interval // 60 + 5, 10)
    result = await fetch_and_send_rss(since_minutes=since_minutes)
    logger.info(f"Cron RSS: {result}")
    return {"status": "ok", **result}


@app.get("/health")
async def health():
    """Проверка здоровья приложения"""
    return {
        "status": "ok",
        "handlers_count": len(handlers),
        "telegram_connected": telegram.client.is_closed is False,
    }


@app.post("/webhook")
async def webhook_endpoint(payload: WebhookPayload):
    """
    Webhook эндпойнт для отправки логов
    
    Example:
        POST /webhook
        {
            "title": "Важное событие",
            "content": "Описание события",
            "url": "https://example.com",
            "tags": ["важное", "тест"]
        }
    """
    try:
        webhook_handler = WebhookHandler("Webhook")
        log_entry = webhook_handler.process_webhook(
            title=payload.title,
            content=payload.content,
            url=payload.url,
            tags=payload.tags,
        )
        
        message = log_entry.format_for_telegram()
        success = await telegram.send_message(message)
        
        if not success:
            raise HTTPException(
                status_code=500,
                detail="Ошибка отправки в Telegram"
            )
        
        return {"status": "sent", "message_id": None}
    
    except Exception as e:
        logger.error(f"Ошибка webhook: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/sources")
async def list_sources():
    """Список активных источников"""
    return {
        "sources": [
            {
                "name": handler.name,
                "type": handler.__class__.__name__,
            }
            for handler in handlers
        ]
    }


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        app,
        host="127.0.0.1",
        port=8000,
        log_level="info" if not settings.debug else "debug",
    )
