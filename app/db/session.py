# app/db/session.py
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.core.config import settings

# 1. Create the engine (The connection to Postgres)
# usage: references DATABASE_URL from your .env file
engine = create_engine(settings.DATABASE_URL)

# 2. Create the SessionLocal class
# Each request will create a new session instance from this factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 3. Dependency Injection (Used in API endpoints)
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()