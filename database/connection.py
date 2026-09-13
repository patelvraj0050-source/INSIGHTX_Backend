import os
from sqlalchemy import create_engine, text

def get_database_url():
    return os.getenv("INSIGHTX_DATABASE_URL", "").strip()

def get_engine():
    url = get_database_url()
    return create_engine(url, pool_pre_ping=True, future=True) if url else None

def test_connection():
    engine = get_engine()
    if engine is None:
        return False, "Database URL not configured."
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        return True, "PostgreSQL connection successful."
    except Exception as exc:
        return False, str(exc)
