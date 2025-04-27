from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import List
import uvicorn
import os
from dotenv import load_dotenv

from .database import get_db, engine
from . import models, schemas
from .data_fetch import update_latest

# Load environment variables
load_dotenv()

# Create database tables
models.Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Trading Bot API",
    description="API for stock market data and trading operations",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {"message": "Welcome to Trading Bot API"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

@app.get("/symbols", response_model=List[schemas.Symbol])
def get_symbols(db: Session = Depends(get_db)):
    symbols = db.query(models.Symbol).all()
    return symbols

@app.get("/data/{symbol}", response_model=List[schemas.MarketData])
def get_market_data(symbol: str, db: Session = Depends(get_db)):
    data = db.query(models.MarketData).filter(models.MarketData.symbol == symbol).all()
    if not data:
        raise HTTPException(status_code=404, detail=f"No data found for symbol {symbol}")
    return data

@app.post("/update")
async def update_data(symbols: List[str], db: Session = Depends(get_db)):
    try:
        updated = update_latest(db, symbols)
        return {"message": f"Successfully updated data for {updated} symbols"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    uvicorn.run(
        "trading_bot.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    ) 