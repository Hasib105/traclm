"""Piccolo ORM Configuration for LLM Tracer."""

from piccolo.conf.apps import AppRegistry
from piccolo.engine.postgres import PostgresEngine
from piccolo.engine.sqlite import SQLiteEngine

from llm_tracer.config import get_settings

settings = get_settings()


def get_engine():
    """Get the database engine based on DATABASE_URL."""
    db_url = settings.database_url
    
    if db_url.startswith("postgresql://"):
        return PostgresEngine(config={"dsn": db_url})
    elif db_url.startswith("sqlite://"):
        # Extract path from sqlite:///path/to/db.sqlite
        db_path = db_url.replace("sqlite:///", "")
        return SQLiteEngine(path=db_path)
    else:
        # Default to SQLite
        return SQLiteEngine(path="llmtracer.db")


DB = get_engine()


# Register Piccolo apps
APP_REGISTRY = AppRegistry(
    apps=[
        "llm_tracer.db.piccolo_app",
    ]
)
