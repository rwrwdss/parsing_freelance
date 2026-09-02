"""
RSS-источники для мониторинга заказов.

plans.MD указывает на freelance.ru (категория 4 — «Веб-разработка и IT»).
У freelance.ru нет RSS для заказов — только для фрилансеров.
Эквивалентные ленты берём с fl.ru (та же биржа, есть RSS).
"""

from dataclasses import dataclass


@dataclass(frozen=True)
class RssFeed:
    name: str
    feed_url: str
    max_items: int = 20
    # Ссылка на страницу категории для справки
    source_page: str = ""


# Категория 4 на freelance.ru → «Веб-разработка и IT»
# Маппинг на fl.ru RSS (см. https://knowledge-base.fl.ru/article/62073)
RSS_FEEDS: list[RssFeed] = [
    RssFeed(
        name="FL.ru — Веб-программирование",
        feed_url="https://www.fl.ru/rss/all.xml?category=5&subcategory=37",
        source_page="https://freelance.ru/task?q=&c%5B%5D=4&a=1&v=1",
    ),
    RssFeed(
        name="FL.ru — Разработка сайтов",
        feed_url="https://www.fl.ru/rss/all.xml?category=2",
        source_page="https://www.fl.ru/projects/",
    ),
    RssFeed(
        name="FL.ru — Программирование",
        feed_url="https://www.fl.ru/rss/all.xml?category=5",
        source_page="https://www.fl.ru/projects/",
    ),
]
