# RSS — IT / backend / mobile

## Сводка по площадкам

| Площадка | RSS заказов | Статус для бота |
|----------|-------------|-----------------|
| [freelance.ru](https://freelance.ru/) | Нет (`/rss`, `/task/rss` → 404) | Через **fl.ru** (общая экосистема) |
| [weblancer.net](https://www.weblancer.net/) | `https://www.weblancer.net/rss/projects.rss` | ❌ Cloudflare 403 с сервера/cron |
| [upwork.com](https://www.upwork.com/) | RSS **отключён** с 20.08.2024 | ❌ Нужен API или сторонний сервис |

---

## freelance.ru → fl.ru (активные ленты)

| Направление | RSS URL | HTTP |
|-------------|---------|------|
| Веб-программирование | `https://www.fl.ru/rss/all.xml?category=5&subcategory=37` | ✅ |
| Сайты под ключ | `https://www.fl.ru/rss/all.xml?category=2&subcategory=27` | ✅ |
| Веб-прогр. (сайты) | `https://www.fl.ru/rss/all.xml?category=2&subcategory=9` | ✅ |
| Backend — прикладное | `https://www.fl.ru/rss/all.xml?category=5&subcategory=1` | ✅ |
| Backend — системное | `https://www.fl.ru/rss/all.xml?category=5&subcategory=2` | ✅ |
| Backend — БД | `https://www.fl.ru/rss/all.xml?category=5&subcategory=5` | ✅ |
| Backend — keyword-фильтр | `https://www.fl.ru/rss/all.xml?category=5` + keywords | ✅ |
| Mobile — keyword-фильтр | `https://www.fl.ru/rss/all.xml?category=5` + keywords | ✅ |
| Mobile / игры (Unity) | `https://www.fl.ru/rss/all.xml?category=16&subcategory=11` | ✅ |

**Mobile:** отдельной стабильной RSS-категории нет — фильтруем ленту `category=5` по ключевым словам (ios, android, flutter, react native и т.д.).

Конфиг: `rss_sources.py` → `RSS_FEEDS`.

---

## weblancer.net

- Официальный URL: `https://www.weblancer.net/rss/projects.rss`
- В браузере может открываться, но с Vercel/GitHub Actions — **403 Cloudflare**
- В `rss_sources.py` помечен `enabled=False` до появления прокси/API

---

## upwork.com

- RSS jobs feed снят: `https://www.upwork.com/ab/feed/jobs/rss` → 403/404
- Альтернатива: [Upwork API](https://www.upwork.com/developer/) или webhook через сторонний парсер

---

## Cron / деплой

| Способ | Интервал | Настройка |
|--------|----------|-----------|
| **GitHub Actions** | каждые 5 мин | `.github/workflows/rss-cron.yml` + secret `CRON_SECRET` |
| **Vercel Cron** | 08:00 UTC ежедневно | `vercel.json` (Hobby plan) |
| **Вручную** | сейчас | `vercel crons run /cron/rss` |

Endpoint: `GET /cron/rss` + `Authorization: Bearer <CRON_SECRET>`

Production: https://parsing-freelance.vercel.app/sources — список всех лент.
