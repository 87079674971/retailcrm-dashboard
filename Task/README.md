# RetailCRM -> Supabase -> Vercel -> Telegram

Демо-проект для задания:

1. загрузить `mock_orders.json` в RetailCRM,
2. синхронизировать заказы из RetailCRM в Supabase,
3. показать дашборд на Vercel,
4. отправлять Telegram-уведомление по заказам выше `50 000 ₸`.

## Стек

- backend и интеграции: `Python`
- serverless API на Vercel: `Python`
- импорт и sync-скрипты: `Python`
- dashboard UI: `HTML + CSS + небольшой browser-side JS`

Полностью без браузерного JavaScript дашборд делать не стала, потому что график и обновление данных удобнее рендерить на клиенте. Вся интеграционная логика при этом переведена на `Python`.

## Что лежит в проекте

- корень репозитория `rc-orders/`
- `api/` — Vercel Python endpoints
- `backend/` — Python-логика для RetailCRM, Supabase, Telegram и агрегаций
- `index.html`, `app.js`, `styles.css` — веб-дашборд
- `requirements.txt` — runtime requirements
- `data/mock_orders.json` — 50 тестовых заказов
- `scripts/import_mock_orders.py` — импорт тестовых заказов в RetailCRM через API
- `scripts/sync_retailcrm_to_supabase.py` — синхронизация RetailCRM -> Supabase
- `supabase/schema.sql` — схема таблиц Supabase
- `api/dashboard.py` — Python endpoint для дашборда
- `api/sync.py` — Python endpoint для ручного full sync
- `api/retailcrm_webhook.py` — Python webhook для trigger из RetailCRM
- `api/health.py` — health endpoint

## Архитектура

`RetailCRM API -> Supabase -> Vercel dashboard`

`RetailCRM trigger -> Vercel Python webhook -> Telegram`

Почему уведомления сделаны через `RetailCRM trigger`, а не через `Vercel Cron`:

- это лучше ложится на бесплатный стек;
- уведомление приходит на событие заказа;
- не нужно ждать расписание cron.

## Шаг 1. Аккаунты

Нужно создать вручную:

- RetailCRM demo: [retailcrm.ru](https://www.retailcrm.ru/)
- Supabase free project: [supabase.com](https://supabase.com/)
- Vercel free account: [vercel.com](https://vercel.com/)
- Telegram bot через `@BotFather`

## Шаг 2. RetailCRM

### Что нужно взять из RetailCRM

- `RETAILCRM_BASE_URL`
  пример: `https://your-subdomain.retailcrm.ru`
- `RETAILCRM_API_KEY`
- `RETAILCRM_SITE_CODE`

Официальная документация RetailCRM:

- [Правила работы с API](https://docs.retailcrm.ru/Developers/API/APIFeatures/APIRules)
- [Раздел по версиям API](https://docs.retailcrm.ru/Developers/API/APIVersions)
- [Возможности trigger-автоматизации](https://docs.retailcrm.ru/Users/Automation/Triggers/TriggerCapabilities)

### Импорт mock_orders.json

Запуск:

```bash
python scripts/import_mock_orders.py \
  --retailcrm-base-url "https://your-subdomain.retailcrm.ru" \
  --retailcrm-api-key "your_api_key" \
  --site-code "your_site_code"
```

Скрипт создает по одному заказу через `POST /api/v5/orders/create`.

## Шаг 3. Supabase

### Что нужно взять из Supabase

- `SUPABASE_URL`
- `SUPABASE_SERVICE_ROLE_KEY`

### Создать таблицы

Открыть SQL Editor и выполнить:

`supabase/schema.sql`

### Синхронизация RetailCRM -> Supabase

Запуск:

```bash
python scripts/sync_retailcrm_to_supabase.py \
  --retailcrm-base-url "https://your-subdomain.retailcrm.ru" \
  --retailcrm-api-key "your_api_key" \
  --site-code "your_site_code" \
  --supabase-url "https://your-project.supabase.co" \
  --supabase-service-role-key "your_service_role_key"
```

Скрипт:

- читает все заказы из RetailCRM по страницам,
- нормализует поля,
- делает upsert в таблицу `orders` через Supabase REST API.

## Шаг 4. Telegram bot

### Создать бота

Через `@BotFather`:

1. `/newbot`
2. получить `TELEGRAM_BOT_TOKEN`

### Получить chat id

1. написать боту любое сообщение
2. открыть:

```text
https://api.telegram.org/bot<YOUR_BOT_TOKEN>/getUpdates
```

3. взять `chat.id`

Официальная документация Telegram:

- [Bot API](https://core.telegram.org/bots/api)
- [BotFather](https://core.telegram.org/bots#botfather)

## Шаг 5. Vercel

### Переменные окружения

Добавить в Vercel:

- `RETAILCRM_BASE_URL`
- `RETAILCRM_API_KEY`
- `RETAILCRM_SITE_CODE`
- `SUPABASE_URL`
- `SUPABASE_SERVICE_ROLE_KEY`
- `TELEGRAM_BOT_TOKEN`
- `TELEGRAM_CHAT_ID`
- `NOTIFICATION_THRESHOLD`
- `WEBHOOK_SECRET`
- `SYNC_SECRET`

Шаблон лежит в `.env.example`.

### Python runtime на Vercel

Используется `Python` runtime Vercel. Официальная документация:

- [Vercel Functions runtimes](https://vercel.com/docs/functions/runtimes)

В проекте добавлены:

- `.python-version`
- `vercel.json`
- `api/*.py`

### Деплой

1. Залить корень репозитория `rc-orders` в GitHub
2. Импортировать репозиторий в Vercel
3. Root Directory не менять, оставить корень репозитория
4. Добавить env-переменные
5. Нажать deploy

После этого дашборд будет доступен по URL Vercel.

## Шаг 6. Настроить уведомления из RetailCRM

В RetailCRM нужно создать trigger с действием `HTTP request`.

URL webhook:

```text
https://YOUR-VERCEL-PROJECT.vercel.app/api/retailcrm_webhook?secret=YOUR_WEBHOOK_SECRET&orderId=<ID заказа>
```

Что делает endpoint:

- забирает полный заказ из RetailCRM API;
- сохраняет его в Supabase;
- если сумма заказа выше `50 000 ₸`, отправляет сообщение в Telegram;
- повторно тот же заказ не уведомляет, потому что запись сохраняется в `telegram_notifications`.

## Ручной full sync через Vercel

Можно вручную дернуть:

```text
https://YOUR-VERCEL-PROJECT.vercel.app/api/sync?secret=YOUR_SYNC_SECRET
```

Endpoint:

- подтягивает все заказы из RetailCRM,
- обновляет Supabase,
- догоняет уведомления по дорогим заказам.

## Что показывает дашборд

Дашборд берет данные с `GET /api/dashboard` и показывает:

- общее число заказов,
- общую выручку,
- средний чек,
- число заказов выше `50 000 ₸`,
- график заказов за последние 14 дней,
- топ городов,
- последние заказы.

## Как выложить в GitHub без локального git

Если на машине нет `git`, можно:

1. создать пустой репозиторий через веб-интерфейс GitHub
2. загрузить содержимое папки `retailcrm-demo` через браузер

## Claude Code notes

`Claude Code` в этой реализации не использовался. Работа велась в `Codex`, поэтому я не стала придумывать несуществующие промпты.

Где среда реально застряла:

- на машине отсутствуют рабочие `git`, `node` и `python`;
- нельзя автоматически пройти регистрацию и логин во внешних сервисах без ручного участия;
- нельзя честно отдать финальные ссылки на Vercel, GitHub и скрин Telegram без реального деплоя и аккаунтов.

Как это было решено:

- интеграции собраны без сторонних Python-зависимостей;
- backend и sync-логика переписаны на `Python`;
- Vercel-роуты сделаны как `Python` functions;
- webhook сделан через `RetailCRM trigger -> Vercel Python endpoint`;
- все секреты вынесены в env-переменные;
- SQL-схема вынесена отдельно для быстрого старта в Supabase.

## Что еще нужно сделать, чтобы получить финальный результат из задания

Нужны реальные внешние действия:

1. создать аккаунты в RetailCRM, Supabase, Vercel и Telegram
2. выполнить `schema.sql` в Supabase
3. импортировать `mock_orders.json` в RetailCRM
4. залить папку `retailcrm-demo` в GitHub
5. задеплоить проект в Vercel
6. создать trigger в RetailCRM на webhook URL
7. сделать тестовый заказ выше `50 000 ₸`
8. открыть Telegram и снять скрин уведомления

После этого можно получить:

- ссылку на Vercel dashboard
- ссылку на GitHub repo
- скриншот уведомления из Telegram
