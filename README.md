# Telegram Logs Bot 📝

Бот для отправки логов из разных источников в Telegram **без задержек** и в реал-тайме.

## Особенности

✅ **RSS источники** — автоматическое отслеживание лент (Freelance.ru, etc)  
✅ **Webhook API** — HTTP API для отправки логов из приложений  
✅ **Файловые логи** — отслеживание новых строк в файлах  
✅ **Async/await** — обработка без блокировки, максимальная скорость  
✅ **Фоновый цикл** — постоянная проверка источников  
✅ **Тесты** — pytest для всех компонентов  

## Установка

```bash
# Клонируем/переходим в папку
cd /Users/amirfatyhov/Desktop/parser

# Создаём виртуальное окружение (Python 3.11–3.14)
python3 -m venv .venv
source .venv/bin/activate   # macOS/Linux
# .venv\Scripts\activate    # Windows

# Устанавливаем зависимости
pip install -r requirements.txt

# Создаём .env файл
cp .env.example .env

# Редактируем .env
# Получаем BOT_TOKEN от BotFather в Telegram
# Получаем CHAT_ID из https://t.me/userinfobot
nano .env
```

## .env конфиг

```env
TELEGRAM_BOT_TOKEN=123456789:ABCDEFGhijklmnopqrstuvwxyz
TELEGRAM_CHAT_ID=987654321
RSS_CHECK_INTERVAL=300  # Проверять каждые 5 минут
DEBUG=false
```

## Использование

### 1️⃣ Запуск сервера

```bash
python main.py

# Или через uvicorn напрямую
uvicorn main:app --reload --host 127.0.0.1 --port 8000
```

Приложение запустится на `http://127.0.0.1:8000`

### 2️⃣ Проверка статуса

```bash
curl http://127.0.0.1:8000/health
```

Ответ:
```json
{
  "status": "ok",
  "handlers_count": 1,
  "telegram_connected": true
}
```

### 3️⃣ Отправка логов через Webhook

```bash
curl -X POST http://127.0.0.1:8000/webhook \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Ошибка в приложении",
    "content": "Database connection failed",
    "url": "https://myapp.com/logs",
    "tags": ["error", "critical"]
  }'
```

### 4️⃣ Просмотр активных источников

```bash
curl http://127.0.0.1:8000/sources
```

Ответ:
```json
{
  "sources": [
    {
      "name": "Freelance.ru (Категория 5)",
      "type": "RSSHandler"
    }
  ]
}
```

## Структура проекта

```
parser/
├── main.py                 # FastAPI приложение + фоновый цикл
├── config.py              # Настройки (из .env)
├── telegram_service.py    # Клиент для Telegram Bot API
├── handlers/
│   ├── base.py           # Базовый класс + LogEntry
│   ├── rss.py            # RSS парсер (Freelance.ru, etc)
│   ├── webhook.py        # HTTP webhook обработчик
│   └── file.py           # Файловые логи
├── tests/
│   ├── test_handlers.py  # Тесты обработчиков
│   └── test_telegram.py  # Тесты Telegram сервиса
├── requirements.txt       # Зависимости
├── .env.example          # Пример конфига
└── README.md             # Этот файл
```

## Как добавить свой RSS источник

В `main.py` добавьте в функцию `initialize_handlers()`:

```python
handlers.append(
    RSSHandler(
        name="Мой источник",
        feed_url="https://example.com/feed.xml",
        max_items=10,  # Сколько последних элементов проверять
    )
)
```

## Как добавить отслеживание файла

```python
from handlers import FileHandler

handlers.append(
    FileHandler(
        name="Логи приложения",
        file_path="/var/log/myapp.log",
    )
)
```

## Запуск тестов

```bash
pytest tests/ -v

# С покрытием
pytest tests/ --cov=handlers --cov=telegram_service
```

## Логирование

Логи выводятся в консоль. Для файловых логов добавьте в `config.py`:

```python
import logging.handlers

handler = logging.handlers.RotatingFileHandler(
    'app.log',
    maxBytes=10_000_000,
    backupCount=5
)
logging.root.addHandler(handler)
```

## Деплой

### На своей машине (forever/systemd)

**systemd сервис:**
```ini
# /etc/systemd/system/telegram-bot.service
[Unit]
Description=Telegram Logs Bot
After=network.target

[Service]
Type=simple
User=ubuntu
WorkingDirectory=/home/ubuntu/parser
Environment="TELEGRAM_BOT_TOKEN=xxx"
Environment="TELEGRAM_CHAT_ID=xxx"
ExecStart=/usr/bin/python3 /home/ubuntu/parser/main.py
Restart=always

[Install]
WantedBy=multi-user.target
```

```bash
sudo systemctl start telegram-bot
sudo systemctl status telegram-bot
sudo journalctl -u telegram-bot -f
```

### На VPS (Docker)

```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

CMD ["python", "main.py"]
```

```bash
docker build -t telegram-bot .
docker run -e TELEGRAM_BOT_TOKEN=xxx -e TELEGRAM_CHAT_ID=xxx telegram-bot
```

## Примеры использования

### Пример 1: Отправка логов из Python приложения

```python
import requests

def log_to_telegram(title, content, url=None):
    requests.post(
        "http://127.0.0.1:8000/webhook",
        json={
            "title": title,
            "content": content,
            "url": url,
            "tags": ["app-log"]
        }
    )

try:
    # Твой код
    pass
except Exception as e:
    log_to_telegram(
        title="Ошибка в приложении",
        content=str(e),
        url="https://myapp.com"
    )
```

### Пример 2: Отправка из bash скрипта

```bash
#!/bin/bash
curl -X POST http://127.0.0.1:8000/webhook \
  -H "Content-Type: application/json" \
  -d "{
    \"title\": \"Резервная копия завершена\",
    \"content\": \"Размер: $(du -h backup.tar.gz | cut -f1)\",
    \"tags\": [\"backup\", \"success\"]
  }"
```

### Пример 3: Отслеживание Freelance.ru задач

Уже настроено в `main.py`! Просто запусти — будет проверять каждые 5 минут и отправлять новые задачи в Telegram.

## Проблемы и решения

| Проблема | Решение |
|----------|---------|
| `ModuleNotFoundError: No module named 'feedparser'` | Запусти `pip install -r requirements.txt` |
| Сообщение не отправляется | Проверь `TELEGRAM_BOT_TOKEN` и `TELEGRAM_CHAT_ID` в `.env` |
| Нет новых логов | Проверь `RSS_CHECK_INTERVAL` — может быть ленты не обновились |
| CORS ошибки | Добавь в `main.py` middleware для CORS если нужно |

## TODO / Фичи для будущего

- [ ] WebSocket для реал-тайм подписки на события
- [ ] Фильтры по ключевым словам (send only если matches)
- [ ] Форматирование по типам (цветные коды, emoji)
- [ ] Database для хранения истории логов
- [ ] Веб-интерфейс для управления источниками
- [ ] Support для других мессенджеров (Discord, Slack)

## Лицензия

MIT
