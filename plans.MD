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

| Способ | Интервал | Настройка |
|--------|----------|-----------|
| **GitHub Actions** | каждые 5 мин | `.github/workflows/rss-cron.yml` + secret `CRON_SECRET` |
| **Vercel Cron** | 08:00 UTC ежедневно | `vercel crons list` / Hobby plan |
| **Вручную** | сейчас | `vercel crons run /cron/rss` |

Endpoint: `GET /cron/rss` + `Authorization: Bearer <CRON_SECRET>`
