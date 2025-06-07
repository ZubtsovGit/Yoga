# Этап сборки
FROM python:3.12.6-slim AS builder

# Установка build-essential для компиляции некоторых пакетов
RUN apt-get update && apt-get upgrade -y && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Создание виртуального окружения
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Копирование и установка зависимостей
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Этап запуска
FROM python:3.12.6-slim AS runner

# Установка только необходимых зависимостей и обновление пакетов безопасности
RUN apt-get update && \
    apt-get upgrade -y && \
    apt-get install -y --no-install-recommends \
    libpq-dev \
    && apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Копирование виртуального окружения из этапа сборки
COPY --from=builder /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Создание непривилегированного пользователя
RUN groupadd -r appuser && useradd -r -g appuser appuser

# Копирование кода приложения
WORKDIR /app
COPY . .

# Назначение владельцем непривилегированного пользователя
RUN chown -R appuser:appuser /app

# Переключение на непривилегированного пользователя
USER appuser

# Установка переменных окружения
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# Команда по умолчанию
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]

# Метаданные для образа
LABEL org.opencontainers.image.source="https://github.com/Predatorevil666/Yoga"
LABEL org.opencontainers.image.description="Application Backend Service for Yoga Platform"
LABEL org.opencontainers.image.licenses="MIT"