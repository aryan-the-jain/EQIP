from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase
from ..config import settings

# For local development, use SQLite if PostgreSQL is not available
try:
    engine = create_engine(settings.database_url, echo=False, future=True)
    # Test connection
    with engine.connect() as conn:
        conn.execute("SELECT 1")
except Exception:
    # Fallback to SQLite for development
    import os
    sqlite_url = "sqlite:///./eqip.db"
    engine = create_engine(sqlite_url, echo=False, future=True)

SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)

class Base(DeclarativeBase):
    pass
