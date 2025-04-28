"""
Dashboard Module

This module creates a Dash-based front-end dashboard that displays live-updating signals,
connecting to the FastAPI server via REST to fetch and display the latest trading signals.
"""

import json

# Dash-based front-end
import logging

import dash
import requests
from dash import dash_table, dcc, html
from dash.dependencies import Input, Output

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Create Dash app
app = dash.Dash(__name__)

# Layout
app.layout = html.Div(
    [
        html.H1("Trading Bot Dashboard"),
        html.Div(
            [
                html.H2("Latest Signals"),
                dash_table.DataTable(
                    id="signals-table",
                    columns=[
                        {"name": "Symbol", "id": "symbol"},
                        {"name": "Timestamp", "id": "timestamp"},
                        {"name": "Signal Type", "id": "signal_type"},
                        {"name": "Reason", "id": "reason"},
                        {"name": "Values", "id": "values"},
                    ],
                    data=[],
                    style_table={"overflowX": "auto"},
                    style_cell={"textAlign": "left", "padding": "10px"},
                    style_header={
                        "backgroundColor": "rgb(230, 230, 230)",
                        "fontWeight": "bold",
                    },
                ),
                dcc.Interval(
                    id="interval-component",
                    interval=5 * 1000,  # Update every 5 seconds
                    n_intervals=0,
                ),
            ]
        ),
    ]
)


# Callback to update the signals table
@app.callback(
    Output("signals-table", "data"), Input("interval-component", "n_intervals")
)
def update_signals(n):
    try:
        response = requests.get("http://localhost:8000/latest")
        if response.status_code == 200:
            signals = response.json()
            for signal in signals:
                signal["reason"] = signal["details"]["reason"]
                signal["values"] = json.dumps(signal["details"]["values"])
            return signals
        else:
            logger.error(f"Failed to fetch signals: {response.status_code}")
            return [
                {
                    "symbol": "Error",
                    "timestamp": "N/A",
                    "signal_type": "N/A",
                    "reason": "Failed to fetch signals",
                    "values": "N/A",
                }
            ]
    except Exception as e:
        logger.error(f"Error updating signals: {e}")
        return [
            {
                "symbol": "Error",
                "timestamp": "N/A",
                "signal_type": "N/A",
                "reason": "Error updating signals",
                "values": "N/A",
            }
        ]


# Run the app
if __name__ == "__main__":
    app.run_server(debug=True, host="0.0.0.0", port=8050)
