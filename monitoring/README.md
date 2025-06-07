# Система мониторинга и логирования для проекта Yoga

В этом документе описана система мониторинга и логирования для проекта Yoga, которая включает:

1. Централизованное логирование (EFK стек и Sentry)
2. Мониторинг метрик (Prometheus + Grafana)
3. Оповещения (AlertManager + Telegram)

## Схема архитектуры

```
┌───────────────┐    ┌───────────────┐    ┌───────────────┐
│    Backend    │    │   Frontend    │    │     Nginx     │
│   Services    │    │   Services    │    │     Proxy     │
└───────┬───────┘    └───────┬───────┘    └───────┬───────┘
        │                    │                    │
        │                    │                    │
┌───────┴────────────────────┴────────────────────┴───────┐
│                                                          │
│                     Docker Network                       │
│                                                          │
└──────┬─────────────────┬──────────────────┬─────────────┘
       │                 │                  │
┌──────┴──────┐   ┌──────┴──────┐    ┌──────┴──────┐
│    EFK      │   │  Prometheus │    │   Sentry    │
│    Stack    │   │  + Grafana  │    │             │
└─────────────┘   └─────────────┘    └─────────────┘
```

## 1. Начало работы

### 1.1 Переменные окружения

Создайте файл `.env` в корне проекта со следующими переменными:

```
# Для Telegram-уведомлений
TELEGRAM_TOKEN=your_telegram_bot_token
TELEGRAM_CHAT_ID=your_telegram_chat_id

# Для Sentry
SENTRY_SECRET_KEY=your_sentry_secret_key
SENTRY_DSN=your_sentry_dsn
```

### 1.2 Запуск системы мониторинга

```bash
# Запуск EFK-стека
cd monitoring/efk
docker-compose up -d

# Запуск Prometheus и Grafana
cd ../prometheus-grafana
docker-compose up -d

# Запуск Sentry (при необходимости)
cd ../sentry
docker-compose up -d
```

## 2. Логирование

### 2.1 Настройка логирования в приложениях

#### Python-бэкенд

```python
from utils.logging import setup_logging

# Инициализация логгера
logger = setup_logging("service-name")

# Использование логгера
logger.info("Это информационное сообщение")
logger.warning("Это предупреждение")
logger.error("Это ошибка", exc_info=True)
logger.debug("Отладочная информация")

# Структурированное логирование
logger.info("Запрос к API", 
    user_id=user.id, 
    endpoint="/api/resource", 
    method="GET",
    response_time=120.5
)

# Логирование ошибок в Sentry
try:
    # Ваш код
    raise ValueError("Что-то пошло не так")
except Exception as e:
    logger.exception("Произошла ошибка", exc_info=True)
```

#### JavaScript-фронтенд

```javascript
// Настройка Sentry
import * as Sentry from '@sentry/react';

Sentry.init({
  dsn: process.env.SENTRY_DSN,
  environment: process.env.NODE_ENV,
  release: "yoga-frontend@" + process.env.VERSION,
  tracesSampleRate: 0.2,
});

// Логирование ошибок
try {
  // Ваш код
} catch (error) {
  Sentry.captureException(error);
  console.error("Произошла ошибка:", error);
}
```

### 2.2 Доступ к логам

- Kibana: http://localhost:5601
- Sentry: http://localhost:9000

## 3. Мониторинг

### 3.1 Настройка метрик в приложениях

#### Python-бэкенд

```python
from utils.metrics import (
    track_request, time_request, 
    track_db_query, time_db_query,
    set_active_users, update_memory_usage,
    start_metrics_server_in_thread
)

# Запуск HTTP-сервера для метрик Prometheus
start_metrics_server_in_thread(port=8000)

# Трекинг HTTP-запросов
@app.middleware("http")
async def metrics_middleware(request, call_next):
    with time_request(request.method, request.url.path) as timer:
        response = await call_next(request)
        track_request(request.method, request.url.path, response.status_code)
    return response

# Трекинг запросов к БД
async def get_user(user_id):
    with time_db_query("SELECT", "users") as timer:
        # Запрос к БД
        track_db_query("SELECT", "users")
        # ...
    return user

# Обновление метрик состояния
def update_app_metrics():
    active_users = get_active_users_count()
    set_active_users(active_users)
    
    memory_usage = get_memory_usage()
    update_memory_usage(memory_usage)
```

### 3.2 Доступ к системе мониторинга

- Prometheus: http://localhost:9090
- Grafana: http://localhost:3000 (admin/admin)
- AlertManager: http://localhost:9093

## 4. Дашборды Grafana

В Grafana предустановлены следующие дашборды:

1. **Yoga System Overview** - общая информация о системе
2. **Yoga Backend Services** - метрики backend-сервисов
3. **Yoga Frontend Services** - метрики frontend-сервисов
4. **Yoga Database** - метрики базы данных
5. **Logs Overview** - обзор логов из Elasticsearch

## 5. Правила оповещений

Настроены следующие правила оповещений:

1. **HighCPULoad** - высокая загрузка CPU (>80% в течение 5 минут)
2. **HighMemoryUsage** - высокое использование памяти (>85% в течение 5 минут)
3. **HighDiskUsage** - высокое использование диска (>85% в течение 5 минут)
4. **ServiceDown** - сервис недоступен (в течение 1 минуты)
5. **HighErrorRate** - высокая частота ошибок HTTP 5xx (>5% в течение 1 минуты)

Все оповещения отправляются в Telegram. 
