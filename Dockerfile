FROM python:3.12-slim

# Установить рабочую директорию
WORKDIR /app

# Копирование зависимостей и файлов проекта
COPY pyproject.toml .
COPY poetry.lock .

# Установка poetry и зависимостей через него
RUN pip install --upgrade pip && pip install poetry
RUN poetry config virtualenvs.create false \
    && poetry install --no-interaction --no-ansi --no-root

# Копирование исходного кода и установка проекта
COPY . .
RUN poetry install --no-interaction --no-ansi

# Открыть порт для приложения
EXPOSE 8000

# Команда запуска (можно переопределить в docker-compose)
CMD alembic upgrade head && \
    uvicorn social_network_api.main:app --host 0.0.0.0 --port 8000 --log-config logconfig.ini
