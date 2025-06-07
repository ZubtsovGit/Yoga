from prometheus_client import Counter, Histogram, Gauge, Summary, start_http_server
import time
import threading
import os

# Метрики для HTTP-запросов
REQUEST_COUNT = Counter(
    'http_requests_total', 
    'Общее количество HTTP запросов',
    ['method', 'endpoint', 'status', 'service']
)

REQUEST_LATENCY = Histogram(
    'http_request_duration_seconds', 
    'Время выполнения HTTP запросов',
    ['method', 'endpoint', 'service'],
    buckets=(0.01, 0.025, 0.05, 0.075, 0.1, 0.25, 0.5, 0.75, 1.0, 2.5, 5.0, 7.5, 10.0, 25.0, 50.0, 75.0, float("inf"))
)

# Метрики для базы данных
DB_QUERY_COUNT = Counter(
    'db_queries_total', 
    'Общее количество запросов к БД',
    ['operation', 'table', 'service']
)

DB_QUERY_LATENCY = Histogram(
    'db_query_duration_seconds', 
    'Время выполнения запросов к БД',
    ['operation', 'table', 'service'],
    buckets=(0.001, 0.005, 0.01, 0.025, 0.05, 0.075, 0.1, 0.25, 0.5, 0.75, 1.0, 2.5, 5.0, float("inf"))
)

# Метрики состояния приложения
ACTIVE_USERS = Gauge(
    'app_active_users',
    'Количество активных пользователей',
    ['service']
)

MEMORY_USAGE = Gauge(
    'app_memory_usage_bytes',
    'Использование памяти приложением',
    ['service']
)

# Получение имени сервиса из переменной окружения или имени хоста
def get_service_name():
    return os.environ.get('SERVICE_NAME', os.environ.get('HOSTNAME', 'unknown'))

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
    service = get_service_name()
    REQUEST_COUNT.labels(method=method, endpoint=endpoint, status=status_code, service=service).inc()

def time_request(method, endpoint):
    """Таймер для измерения времени выполнения HTTP-запроса"""
    service = get_service_name()
    return TimerContextManager(REQUEST_LATENCY, [method, endpoint, service])

def track_db_query(operation, table):
    """Отслеживание запроса к БД"""
    service = get_service_name()
    DB_QUERY_COUNT.labels(operation=operation, table=table, service=service).inc()

def time_db_query(operation, table):
    """Таймер для измерения времени выполнения запроса к БД"""
    service = get_service_name()
    return TimerContextManager(DB_QUERY_LATENCY, [operation, table, service])

def set_active_users(count):
    """Установка значения активных пользователей"""
    service = get_service_name()
    ACTIVE_USERS.labels(service=service).set(count)

def update_memory_usage(usage_bytes):
    """Обновление значения использования памяти"""
    service = get_service_name()
    MEMORY_USAGE.labels(service=service).set(usage_bytes)

# Запуск HTTP-сервера для метрик Prometheus
def start_metrics_server(port=8000):
    """Запуск HTTP-сервера для метрик Prometheus"""
    try:
        start_http_server(port)
        print(f"Metrics server started on port {port}")
    except Exception as e:
        print(f"Failed to start metrics server: {e}")
    
# Функция для запуска HTTP-сервера в отдельном потоке
def start_metrics_server_in_thread(port=8000):
    """Запуск HTTP-сервера для метрик Prometheus в отдельном потоке"""
    thread = threading.Thread(
        target=start_metrics_server,
        args=(port,),
        daemon=True
    )
    thread.start()
    print(f"Started metrics server thread on port {port}")
    return thread 
