from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)

try:
    db = SessionLocal()
    print("✅ Connected to PostgreSQL database!")
    db.close()
except Exception as e:
    print("❌ Failed to connect:", e)

