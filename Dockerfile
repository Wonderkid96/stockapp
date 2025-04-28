# Dockerfile for Trading Bot
FROM python:3.8-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install Poetry
RUN curl -sSL https://install.python-poetry.org | python3 -

# Set working directory
WORKDIR /app

# Copy project files
COPY pyproject.toml poetry.lock ./
COPY src/ ./src/

# Install dependencies
RUN poetry config virtualenvs.create false \
    && poetry install --no-interaction --no-ansi --no-root

# Install the project
RUN poetry install --no-interaction --no-ansi

# Run the application
CMD ["poetry", "run", "uvicorn", "stockapp.main:app", "--host", "0.0.0.0", "--port", "8000"] 