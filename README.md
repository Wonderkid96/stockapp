# Python Trading Bot

A comprehensive Python-based trading bot that implements various technical analysis strategies and executes trades through the Alpaca API.

## Features

- Real-time market data ingestion using yfinance
- Technical indicators calculation (SMA, EMA, RSI, MACD)
- Signal generation based on multiple strategies
- Backtesting engine for strategy validation
- Paper trading and live trading support
- FastAPI-based REST API and WebSocket server
- Interactive Dash dashboard for monitoring
- TimescaleDB for efficient time-series data storage
- Docker support for easy deployment
- Comprehensive test suite
- Pre-commit hooks for code quality
- CI/CD pipeline

## Prerequisites

- Python 3.9+
- PostgreSQL with TimescaleDB extension
- Docker and Docker Compose (optional)
- Alpaca API credentials

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/trading-bot.git
cd trading-bot
```

2. Create and activate a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# or
.\venv\Scripts\activate  # Windows
```

3. Install dependencies:
```bash
make install
```

4. Copy the example environment file and configure it:
```bash
cp .env.example .env
# Edit .env with your configuration
```

5. Initialize the database:
```bash
make db-migrate
```

## Usage

### Development

1. Start the development server:
```bash
make dev
```

2. Run tests:
```bash
make test
```

3. Format code:
```bash
make format
```

4. Run linters:
```bash
make lint
```

### Docker

1. Build and run with Docker Compose:
```bash
make docker-build
make docker-run
```

### API Endpoints

- `GET /health` - Health check
- `GET /latest` - Get latest trading signals
- `GET /historical/{symbol}` - Get historical price data
- `GET /indicators/{symbol}` - Get technical indicators
- `WS /ws` - WebSocket for real-time updates

### Dashboard

Access the interactive dashboard at `http://localhost:8050` after starting the application.

## Project Structure

```
trading_bot/
├── app.py              # FastAPI application
├── backtest.py         # Backtesting engine
├── data_fetch.py       # Market data ingestion
├── db_models.py        # Database models
├── executor.py         # Trade execution
├── indicators.py       # Technical indicators
├── signal_engine.py    # Signal generation
└── dashboard.py        # Dash dashboard

tests/
├── conftest.py         # Test fixtures
├── test_app.py         # API tests
├── test_backtest.py    # Backtesting tests
├── test_data_fetch.py  # Data fetching tests
├── test_db_models.py   # Database tests
├── test_executor.py    # Execution tests
├── test_indicators.py  # Indicator tests
└── test_signal_engine.py # Signal engine tests
```

## Testing

The project includes a comprehensive test suite:

```bash
# Run all tests
make test

# Run tests with coverage
make test-coverage

# Run tests in watch mode
make test-watch
```

## Code Quality

The project uses several tools to maintain code quality:

- Black for code formatting
- Flake8 for linting
- MyPy for type checking
- Bandit for security checks
- Safety for dependency checks
- Pre-commit hooks for automated checks

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- [Alpaca](https://alpaca.markets/) for the trading API
- [yfinance](https://github.com/ranaroussi/yfinance) for market data
- [FastAPI](https://fastapi.tiangolo.com/) for the web framework
- [Dash](https://plotly.com/dash/) for the dashboard
- [TimescaleDB](https://www.timescale.com/) for time-series data storage 