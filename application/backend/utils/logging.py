import os
import logging
import structlog
import sentry_sdk
from fluent import sender, handler
from sentry_sdk.integrations.logging import LoggingIntegration

# Конфигурация Sentry
def init_sentry():
    sentry_dsn = os.environ.get("SENTRY_DSN")
    if sentry_dsn:
        sentry_logging = LoggingIntegration(
            level=logging.INFO,  # Захват логов уровня INFO и выше
            event_level=logging.ERROR  # Отправка в Sentry событий уровня ERROR и выше
        )

        sentry_sdk.init(
            dsn=sentry_dsn,
            integrations=[sentry_logging],
            traces_sample_rate=0.2,  # Процент трассировок для производительности
            environment=os.environ.get("ENVIRONMENT", "development"),
            release=os.environ.get("APP_VERSION", "dev"),
        )
        
        return True
    return False

# Конфигурация Fluentd
def init_fluentd_logger(app_name):
    fluentd_host = os.environ.get("FLUENTD_HOST", "fluentd")
    fluentd_port = int(os.environ.get("FLUENTD_PORT", 24224))
    
    custom_format = {
        "level": "%(levelname)s",
        "hostname": "%(hostname)s",
        "service": app_name,
        "where": "%(module)s.%(funcName)s",
        "message": "%(message)s",
    }
    
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )
    
    # Настройка логгера для Fluentd
    fluent_handler = handler.FluentHandler(
        f'yoga.{app_name}',
        host=fluentd_host,
        port=fluentd_port
    )
    
    formatter = handler.FluentRecordFormatter(custom_format)
    fluent_handler.setFormatter(formatter)
    
    root_logger = logging.getLogger()
    root_logger.addHandler(fluent_handler)
    
    # Настройка структурированного логирования
    structlog.configure(
        processors=[
            structlog.stdlib.filter_by_level,
            structlog.stdlib.add_logger_name,
            structlog.stdlib.add_log_level,
            structlog.stdlib.PositionalArgumentsFormatter(),
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.StackInfoRenderer(),
            structlog.processors.format_exc_info,
            structlog.processors.UnicodeDecoder(),
            structlog.stdlib.render_to_log_kwargs,
        ],
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )
    
    return structlog.get_logger()

# Функция инициализации логирования
def setup_logging(app_name="application-backend"):
    sentry_initialized = init_sentry()
    logger = init_fluentd_logger(app_name)
    
    logger.info(
        "Логирование настроено", 
        sentry_enabled=sentry_initialized, 
        app_name=app_name
    )
    
    return logger
