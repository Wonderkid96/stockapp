import typer

from stockapp.dashboard import main as start_dashboard  # Placeholder
from stockapp.main import run_live

# from stockapp.backtests.backtest_engine import run_backtest  # Placeholder

app = typer.Typer(help="StockApp CLI")


@app.command()
def scan():
    """Run the pre-market scanner and list today's tickers."""
    # Placeholder: Replace with actual scan logic
    typer.echo("Running premarket scan...")
    # premarket_scan(...)


@app.command()
def backtest(
    start: str = typer.Option(..., help="YYYY-MM-DD"),
    end: str = typer.Option(..., help="YYYY-MM-DD"),
):
    """Run a historical backtest over the given date range."""
    typer.echo(f"Running backtest from {start} to {end}...")
    # run_backtest(start, end)


@app.command()
def live(paper: bool = typer.Option(True, help="Paper trade if true")):
    """Start the live trading loop."""
    typer.echo(f"Starting live trading. Paper: {paper}")
    run_live(paper)


@app.command()
def dashboard(port: int = 8050):
    """Launch the monitoring dashboard."""
    typer.echo(f"Starting dashboard on port {port}...")
    start_dashboard(port)


if __name__ == "__main__":
    app()
