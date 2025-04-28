from typing import List

import uvicorn
from dotenv import load_dotenv
from fastapi import Depends, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

from . import schemas
from .data_fetch import update_latest
from .database import engine, get_db
from .db_models import Base, RawPrice

# Load environment variables
load_dotenv()

# Create database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Trading Bot API",
    description="API for stock market data and trading operations",
    version="1.0.0",
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
    symbols = db.query(RawPrice).all()
    return symbols


@app.get("/data/{symbol}", response_model=List[schemas.MarketData])
def get_market_data(symbol: str, db: Session = Depends(get_db)):
    data = db.query(RawPrice).filter(RawPrice.symbol == symbol).all()
    if not data:
        raise HTTPException(
            status_code=404, detail=f"No data found for symbol {symbol}"
        )
    return data


@app.post("/update")
async def update_data(symbols: List[str], db: Session = Depends(get_db)):
    try:
        updated = update_latest(db, symbols)
        return {"message": f"Successfully updated data for {updated} symbols"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    uvicorn.run("stockapp.main:app", host="0.0.0.0", port=8000, reload=True)
