"""Piccolo ORM configuration.

This configuration supports both PostgreSQL and SQLite databases.
Set environment variables to use PostgreSQL, otherwise SQLite is used by default.

Environment Variables:
    DATABASE_URL: Full PostgreSQL connection URL (preferred)
                  Format: postgresql://user:password@host:port/database

    Or individual settings:
    POSTGRES_HOST: PostgreSQL host (default: localhost)
    POSTGRES_PORT: PostgreSQL port (default: 5432)
    POSTGRES_USER: PostgreSQL username
    POSTGRES_PASSWORD: PostgreSQL password
    POSTGRES_DB: PostgreSQL database name (default: llm_tracer)

    SQLITE_PATH: SQLite database path (default: ./llm_tracer.db)
"""

import os
from urllib.parse import urlparse

from piccolo.conf.apps import AppRegistry


def get_db_engine():
    """Get the appropriate database engine based on environment configuration.

    Priority:
    1. DATABASE_URL environment variable (PostgreSQL)
    2. POSTGRES_* environment variables (PostgreSQL)
    3. SQLite fallback (default)

    Returns:
        Engine instance (PostgresEngine or SQLiteEngine)
    """
    database_url = os.environ.get("DATABASE_URL")

    if database_url:
        # Parse DATABASE_URL for PostgreSQL
        return _create_postgres_engine_from_url(database_url)

    # Check for individual PostgreSQL config
    postgres_host = os.environ.get("POSTGRES_HOST")
    postgres_user = os.environ.get("POSTGRES_USER")

    if postgres_host and postgres_user:
        return _create_postgres_engine_from_env()

    # Fallback to SQLite
    return _create_sqlite_engine()


def _create_postgres_engine_from_url(url: str):
    """Create PostgreSQL engine from DATABASE_URL."""
    from piccolo.engine.postgres import PostgresEngine

    parsed = urlparse(url)

    config = {
        "host": parsed.hostname or "localhost",
        "port": parsed.port or 5432,
        "user": parsed.username,
        "password": parsed.password,
        "database": parsed.path.lstrip("/") or "llm_tracer",
    }

    return PostgresEngine(config=config)


def _create_postgres_engine_from_env():
    """Create PostgreSQL engine from individual environment variables."""
    from piccolo.engine.postgres import PostgresEngine

    config = {
        "host": os.environ.get("POSTGRES_HOST", "localhost"),
        "port": int(os.environ.get("POSTGRES_PORT", "5432")),
        "user": os.environ.get("POSTGRES_USER"),
        "password": os.environ.get("POSTGRES_PASSWORD"),
        "database": os.environ.get("POSTGRES_DB", "llm_tracer"),
    }

    return PostgresEngine(config=config)


def _create_sqlite_engine():
    """Create SQLite engine (default fallback)."""
    from piccolo.engine.sqlite import SQLiteEngine

    path = os.environ.get("SQLITE_PATH", "./llm_tracer.db")
    return SQLiteEngine(path=path)


# Initialize the database engine
DB = get_db_engine()

# Register Piccolo apps
APP_REGISTRY = AppRegistry(apps=["llm_tracer.db.piccolo_app"])
