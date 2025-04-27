import os
from sqlalchemy import create_engine
from dotenv import load_dotenv

load_dotenv()
db_url = os.getenv("DATABASE_URL")

if not db_url:
    print("DATABASE_URL not set!")
    exit(1)

try:
    engine = create_engine(db_url)
    with engine.connect() as conn:
        result = conn.execute("SELECT 1;")
        print("Database connection successful! Result:", result.scalar())
except Exception as e:
    print("Database connection failed:", e) 