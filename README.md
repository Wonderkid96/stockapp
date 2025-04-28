# StockApp

A professional-grade, modular stock trading and analysis platform with live and historical data, robust risk management, and modern Python packaging.

## Overview
StockApp is a research and trading platform supporting live and historical data, modular strategies, risk management, and real-time alerts. It is designed for both backtesting and live trading, with a focus on maintainability and extensibility.

## Prerequisites
- Python 3.10+
- Docker (for TimescaleDB/Postgres)
- (Optional) Poetry for dependency management

## Configuration
- All settings are in `config/settings.yaml` (see `config/settings.yaml.example` for template)
- Environment variables for secrets (API keys, Slack webhook, etc.)

## Quickstart
```bash
# 1. Copy and edit config
cp config/settings.yaml.example config/settings.yaml

# 2. Start database
make docker-run

# 3. Install dependencies
pip install -r requirements.txt

# 4. Run Alembic migrations
make alembic-upgrade

# 5. Run the app
python -m stockapp.main
```

## Architecture
```
+-------------------+
|  config/settings  |
+-------------------+
          |
+-------------------+
|   src/stockapp/   |
+-------------------+
| strategies/       |
| risk_manager.py   |
| scanner.py        |
| ...               |
+-------------------+
          |
+-------------------+
|   data/           |
+-------------------+
| etoro_tickers.txt |
| ...               |
+-------------------+
```

- Modular strategies in `src/stockapp/strategies/`
- Risk management in `src/stockapp/risk_manager.py`
- Logging and Slack alerts in `src/logger.py`
- Database migrations with Alembic

## Badges
- [![Build Status](https://img.shields.io/github/actions/workflow/status/Wonderkid96/stockapp/python-app.yml?branch=main)](https://github.com/Wonderkid96/stockapp/actions)
- [![Coverage Status](https://img.shields.io/codecov/c/github/Wonderkid96/stockapp)](https://codecov.io/gh/Wonderkid96/stockapp)
- [![Docker](https://img.shields.io/docker/pulls/Wonderkid96/stockapp)](https://hub.docker.com/r/Wonderkid96/stockapp)

## License
MIT 

## Environment Variables

The following environment variables are required:

### Required Variables
- `DATABASE_URL`: PostgreSQL connection string
- `ALPACA_API_KEY`: Your Alpaca API key
- `ALPACA_API_SECRET`: Your Alpaca API secret
- `SECRET_KEY`: Secret key for JWT tokens (generate with: `openssl rand -hex 32`)

### Optional Variables
- `YFINANCE_BACKFILL_CHUNK`: Number of days to fetch in each backfill request (default: 100)
- `POLLING_INTERVAL`: Seconds between market data updates (default: 60)
- `LOG_LEVEL`: Logging level (default: INFO)
- `SENTRY_DSN`: Sentry DSN for error tracking
- `CORS_ORIGINS`: Comma-separated list of allowed origins
- `REDIS_URL`: Redis connection for task queue
- `TEST_DATABASE_URL`: Database URL for testing 