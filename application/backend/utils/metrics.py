from prometheus_client import Counter, Histogram, Gauge, Summary, start_http_server
import time
import threading

# Метрики для HTTP-запросов
REQUEST_COUNT = Counter(
    'http_requests_total', 
    'Общее количество HTTP запросов',
    ['method', 'endpoint', 'status']
)

REQUEST_LATENCY = Histogram(
    'http_request_duration_seconds', 
    'Время выполнения HTTP запросов',
    ['method', 'endpoint'],
    buckets=(0.01, 0.025, 0.05, 0.075, 0.1, 0.25, 0.5, 0.75, 1.0, 2.5, 5.0, 7.5, 10.0, 25.0, 50.0, 75.0, float("inf"))
)

# Метрики для базы данных
DB_QUERY_COUNT = Counter(
    'db_queries_total', 
    'Общее количество запросов к БД',
    ['operation', 'table']
)

DB_QUERY_LATENCY = Histogram(
    'db_query_duration_seconds', 
    'Время выполнения запросов к БД',
    ['operation', 'table'],
    buckets=(0.001, 0.005, 0.01, 0.025, 0.05, 0.075, 0.1, 0.25, 0.5, 0.75, 1.0, 2.5, 5.0, float("inf"))
)

# Метрики состояния приложения
ACTIVE_USERS = Gauge(
    'app_active_users',
    'Количество активных пользователей'
)

MEMORY_USAGE = Gauge(
    'app_memory_usage_bytes',
    'Использование памяти приложением'
)

# Класс-таймер для измерения времени выполнения операций
class TimerContextManager:
    def __init__(self, metric, labels):
        self.metric = metric
        self.labels = labels
        
    def __enter__(self):
        self.start = time.time()
        return self
        
    def __exit__(self, exc_type, exc_val, exc_tb):
        duration = time.time() - self.start
        self.metric.labels(*self.labels).observe(duration)


# Функции-хелперы для работы с метриками
def track_request(method, endpoint, status_code):
    """Отслеживание HTTP-запроса"""
    REQUEST_COUNT.labels(method=method, endpoint=endpoint, status=status_code).inc()

def time_request(method, endpoint):
    """Таймер для измерения времени выполнения HTTP-запроса"""
    return TimerContextManager(REQUEST_LATENCY, [method, endpoint])

def track_db_query(operation, table):
    """Отслеживание запроса к БД"""
    DB_QUERY_COUNT.labels(operation=operation, table=table).inc()

def time_db_query(operation, table):
    """Таймер для измерения времени выполнения запроса к БД"""
    return TimerContextManager(DB_QUERY_LATENCY, [operation, table])

def set_active_users(count):
    """Установка значения активных пользователей"""
    ACTIVE_USERS.set(count)

def update_memory_usage(usage_bytes):
    """Обновление значения использования памяти"""
    MEMORY_USAGE.set(usage_bytes)

# Запуск HTTP-сервера для метрик Prometheus
def start_metrics_server(port=8000):
    """Запуск HTTP-сервера для метрик Prometheus"""
    start_http_server(port)
    
# Функция для запуска HTTP-сервера в отдельном потоке
def start_metrics_server_in_thread(port=8000):
    """Запуск HTTP-сервера для метрик Prometheus в отдельном потоке"""
    thread = threading.Thread(
        target=start_metrics_server,
        args=(port,),
        daemon=True
    )
    thread.start()
    return thread
