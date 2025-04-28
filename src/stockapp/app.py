"""
FastAPI Server Module

This module creates a FastAPI server with REST and WebSocket endpoints for real-time signal updates,
providing a GET /latest endpoint and a WebSocket /ws endpoint for streaming new signals.
"""

import asyncio

# FastAPI server (REST & WS)
import logging

from fastapi import Depends, FastAPI, HTTPException, WebSocket
from sqlalchemy.orm import Session
from fastapi.middleware.cors import CORSMiddleware
from .database import get_db
from .db_models import Signal, init_db
from .schemas import Signal as SignalSchema

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="Trading Bot API",
    description="API for stock market data and trading operations",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8050"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize database tables on startup
@app.on_event("startup")
async def startup_event():
    init_db()
    logger.info("Database tables initialized.")


# Dependency to get DB session
def get_db_session():
    db = next(get_db())
    try:
        yield db
    finally:
        db.close()


# Root endpoint
@app.get("/")
async def root():
    return {
        "message": "Welcome to Trading Bot API",
        "endpoints": {
            "root": "/",
            "health": "/health",
            "latest_signals": "/latest",
            "websocket": "/ws",
        },
    }


# Health check endpoint
@app.get("/health")
def health_check():
    """Health check endpoint."""
    return {"status": "ok"}


# REST endpoint to get latest signals
@app.get("/latest")
async def get_latest_signals(db: Session = Depends(get_db_session)):
    try:
        signals = (
            db.query(Signal)
            .order_by(Signal.timestamp.desc())
            .limit(20)
            .all()
        )
        return [SignalSchema.from_orm(signal) for signal in signals]
    except Exception as e:
        logger.error(f"Error fetching latest signals: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


# WebSocket endpoint to stream new signals
@app.websocket("/ws")
async def websocket_endpoint(
    websocket: WebSocket, db: Session = Depends(get_db_session)
):
    await websocket.accept()
    logger.info("WebSocket connection established.")
    last_id = 0
    while True:
        try:
            # Poll for new signals
            new_signals = (
                db.query(Signal)
                .filter(Signal.id > last_id)
                .order_by(Signal.timestamp.asc())
                .all()
            )
            for signal in new_signals:
                await websocket.send_json(
                    {
                        "symbol": signal.symbol,
                        "timestamp": signal.timestamp,
                        "signal_type": signal.signal_type,
                        "details": signal.details,
                    }
                )
                last_id = signal.id
            # Sleep to avoid hammering the database
            await asyncio.sleep(5)
        except Exception as e:
            logger.error(f"WebSocket error: {e}")
            await websocket.close()
            break


# Example usage
if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
