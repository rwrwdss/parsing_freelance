"""
RSS-источники для IT / backend / mobile.

freelance.ru — RSS заказов нет; используем fl.ru (общая экосистема).
weblancer.net — лента projects.rss есть, но Cloudflare блокирует serverless/cron.
upwork.com — RSS отключён с 20.08.2024.
"""

from dataclasses import dataclass, field


@dataclass(frozen=True)
class RssFeed:
    name: str
    feed_url: str
    max_items: int = 30
    source_page: str = ""
    platform: str = ""
    keywords: tuple[str, ...] = field(default_factory=tuple)
    enabled: bool = True


MOBILE_KEYWORDS = (
    "mobile",
    "мобильн",
    "ios",
    "android",
    "flutter",
    "react native",
    "react-native",
    "kotlin",
    "swift",
    "swiftui",
    "xamarin",
    "unity",
    "telegram mini app",
    "приложен",
)

BACKEND_KEYWORDS = (
    "backend",
    "бэкенд",
    "back-end",
    "api",
    "rest",
    "graphql",
    "django",
    "fastapi",
    "flask",
    "laravel",
    "node.js",
    "nodejs",
    "python",
    "golang",
    "postgres",
    "mysql",
    "redis",
    "микросервис",
    "сервер",
)

RSS_FEEDS: list[RssFeed] = [
    # --- freelance.ru / fl.ru — Веб-разработка и IT ---
    RssFeed(
        name="Freelance/FL — Веб-программирование",
        platform="freelance.ru",
        feed_url="https://www.fl.ru/rss/all.xml?category=5&subcategory=37",
        source_page="https://freelance.ru/task?q=&c%5B%5D=4&a=1&v=1",
    ),
    RssFeed(
        name="Freelance/FL — Сайты под ключ",
        platform="freelance.ru",
        feed_url="https://www.fl.ru/rss/all.xml?category=2&subcategory=27",
        source_page="https://freelance.ru/task?q=&c%5B%5D=4&a=1&v=1",
    ),
    RssFeed(
        name="Freelance/FL — Веб-программирование (сайты)",
        platform="freelance.ru",
        feed_url="https://www.fl.ru/rss/all.xml?category=2&subcategory=9",
        source_page="https://www.fl.ru/projects/category/sayty/",
    ),
    # --- Backend ---
    RssFeed(
        name="Freelance/FL — Backend (прикладное программирование)",
        platform="freelance.ru",
        feed_url="https://www.fl.ru/rss/all.xml?category=5&subcategory=1",
        source_page="https://www.fl.ru/projects/category/programmirovanie/",
    ),
    RssFeed(
        name="Freelance/FL — Backend (системное программирование)",
        platform="freelance.ru",
        feed_url="https://www.fl.ru/rss/all.xml?category=5&subcategory=2",
        source_page="https://www.fl.ru/projects/category/programmirovanie/",
    ),
    RssFeed(
        name="Freelance/FL — Backend (базы данных)",
        platform="freelance.ru",
        feed_url="https://www.fl.ru/rss/all.xml?category=5&subcategory=5",
        source_page="https://www.fl.ru/projects/category/programmirovanie/",
    ),
    RssFeed(
        name="Freelance/FL — Backend (фильтр по ключевым словам)",
        platform="freelance.ru",
        feed_url="https://www.fl.ru/rss/all.xml?category=5",
        source_page="https://www.fl.ru/projects/category/programmirovanie/",
        keywords=BACKEND_KEYWORDS,
        max_items=60,
    ),
    # --- Mobile ---
    RssFeed(
        name="Freelance/FL — Мобильные приложения (фильтр)",
        platform="freelance.ru",
        feed_url="https://www.fl.ru/rss/all.xml?category=5",
        source_page="https://www.fl.ru/projects/category/mobile/",
        keywords=MOBILE_KEYWORDS,
        max_items=60,
    ),
    RssFeed(
        name="Freelance/FL — Mobile / игры (Unity, моб. игры)",
        platform="freelance.ru",
        feed_url="https://www.fl.ru/rss/all.xml?category=16&subcategory=11",
        source_page="https://www.fl.ru/projects/category/mobile/",
    ),
    # --- weblancer.net — отключено: Cloudflare 403 с сервера ---
    RssFeed(
        name="Weblancer — все проекты",
        platform="weblancer.net",
        feed_url="https://www.weblancer.net/rss/projects.rss",
        source_page="https://www.weblancer.net/freelance/",
        enabled=False,
    ),
    # --- upwork.com — RSS снят ---
    RssFeed(
        name="Upwork — jobs RSS (deprecated)",
        platform="upwork.com",
        feed_url="https://www.upwork.com/ab/feed/jobs/rss",
        source_page="https://www.upwork.com/",
        enabled=False,
    ),
]
