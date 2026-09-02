# RSS — категории и источники

## Целевая категория (из plans.MD)

| Параметр | Значение |
|----------|----------|
| Сайт | [freelance.ru](https://freelance.ru) |
| Категория | **4 — Веб-разработка и IT** |
| Страница фильтра | https://freelance.ru/task?q=&c%5B%5D=4&a=1&v=1 |

## RSS на freelance.ru

**Заказы:** RSS **нет** ( `/rss`, `/task/rss` → 404 ).

**Фрилансеры:** есть HTML-страница https://freelance.ru/freelancers/rss — не подходит для мониторинга заказов.

## RSS на fl.ru (используем для бота)

| Категория | RSS URL | Статус |
|-----------|---------|--------|
| Веб-программирование (cat=5, sub=37) | https://www.fl.ru/rss/all.xml?category=5&subcategory=37 | ✅ 200 |
| Разработка сайтов (cat=2) | https://www.fl.ru/rss/all.xml?category=2 | ✅ 200 |
| Программирование (cat=5) | https://www.fl.ru/rss/all.xml?category=5 | ✅ 200 |

## Cron

- Endpoint: `GET /cron/rss` + header `Authorization: Bearer <CRON_SECRET>`
- **Vercel Cron (Hobby):** 1 раз в день в 08:00 UTC (`0 8 * * *`)
- **Каждые 5 мин (рекомендуется):** [cron-job.org](https://cron-job.org) → URL `https://parsing-freelance.vercel.app/cron/rss`, интервал 5 мин, header `Authorization: Bearer <CRON_SECRET>`
