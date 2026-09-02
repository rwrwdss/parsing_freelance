import asyncio
import logging
import os
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from contextlib import asynccontextmanager

from config import settings
from telegram_service import telegram
from handlers import RSSHandler, WebhookHandler, LogEntry

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
    
    # RSS обработчики
    handlers.append(
        RSSHandler(
            name="Freelance.ru (Категория 5)",
            feed_url="https://www.fl.ru/rss/?category=5",
            max_items=10,
        )
    )
    
    # Можно добавить другие RSS ленты:
    # handlers.append(
    #     RSSHandler(
    #         name="Другой источник",
    #         feed_url="https://example.com/feed",
    #     )
    # )
    
    logger.info(f"Инициализировано {len(handlers)} обработчиков")


async def background_fetch_loop():
    """Фоновый цикл для проверки новых логов"""
    logger.info("Запущен фоновый цикл проверки логов")
    
    while True:
        try:
            for handler in handlers:
                try:
                    logs = await handler.fetch()
                    for log in logs:
                        # Отправляем каждый лог в Telegram
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
    }


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
