"""Piccolo ORM configuration."""

import os

from piccolo.conf.apps import AppRegistry
from piccolo.engine.postgres import PostgresEngine
from piccolo.engine.sqlite import SQLiteEngine

# Determine database engine based on environment
DATABASE_URL = os.environ.get("DATABASE_URL", "")

if DATABASE_URL.startswith("postgresql://") or DATABASE_URL.startswith("postgres://"):
    # PostgreSQL configuration
    DB = PostgresEngine(
        config={
            "dsn": DATABASE_URL,
        }
    )
elif os.environ.get("POSTGRES_HOST"):
    # PostgreSQL from individual env vars
    DB = PostgresEngine(
        config={
            "host": os.environ.get("POSTGRES_HOST", "localhost"),
            "port": int(os.environ.get("POSTGRES_PORT", "5432")),
            "user": os.environ.get("POSTGRES_USER", "postgres"),
            "password": os.environ.get("POSTGRES_PASSWORD", "postgres"),
            "database": os.environ.get("POSTGRES_DB", "llm_tracer"),
        }
    )
else:
    # SQLite fallback for development
    db_path = os.environ.get("SQLITE_PATH", "./llm_tracer.db")
    DB = SQLiteEngine(path=db_path)

APP_REGISTRY = AppRegistry(apps=["llm_tracer.db.piccolo_app"])
