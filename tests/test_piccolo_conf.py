"""Tests for Piccolo configuration."""

import os
from unittest.mock import patch


class TestPiccoloConfig:
    """Tests for database configuration."""

    def test_default_sqlite_engine(self):
        """Test default SQLite engine is used."""
        with patch.dict(os.environ, {}, clear=True):
            # Re-import to get fresh config
            from piccolo.engine.sqlite import SQLiteEngine
            from piccolo_conf import get_db_engine

            engine = get_db_engine()
            assert isinstance(engine, SQLiteEngine)

    def test_postgres_from_database_url(self):
        """Test PostgreSQL from DATABASE_URL."""
        with patch.dict(
            os.environ, {"DATABASE_URL": "postgresql://user:pass@localhost:5432/testdb"}, clear=True
        ):
            from piccolo.engine.postgres import PostgresEngine
            from piccolo_conf import _create_postgres_engine_from_url

            engine = _create_postgres_engine_from_url(
                "postgresql://user:pass@localhost:5432/testdb"
            )
            assert isinstance(engine, PostgresEngine)

    def test_postgres_from_env_vars(self):
        """Test PostgreSQL from individual env vars."""
        with patch.dict(
            os.environ,
            {
                "POSTGRES_HOST": "localhost",
                "POSTGRES_PORT": "5432",
                "POSTGRES_USER": "testuser",
                "POSTGRES_PASSWORD": "testpass",
                "POSTGRES_DB": "testdb",
            },
            clear=True,
        ):
            from piccolo.engine.postgres import PostgresEngine
            from piccolo_conf import _create_postgres_engine_from_env

            engine = _create_postgres_engine_from_env()
            assert isinstance(engine, PostgresEngine)

    def test_custom_sqlite_path(self):
        """Test custom SQLite path from env var."""
        with patch.dict(os.environ, {"SQLITE_PATH": "./custom.db"}, clear=True):
            from piccolo.engine.sqlite import SQLiteEngine
            from piccolo_conf import _create_sqlite_engine

            engine = _create_sqlite_engine()
            assert isinstance(engine, SQLiteEngine)

    def test_database_url_parsing(self):
        """Test DATABASE_URL parsing."""
        from piccolo_conf import _create_postgres_engine_from_url

        url = "postgresql://myuser:mypass@db.example.com:5433/mydb"
        engine = _create_postgres_engine_from_url(url)

        assert engine.config["host"] == "db.example.com"
        assert engine.config["port"] == 5433
        assert engine.config["user"] == "myuser"
        assert engine.config["password"] == "mypass"
        assert engine.config["database"] == "mydb"

    def test_database_url_defaults(self):
        """Test DATABASE_URL with defaults."""
        from piccolo_conf import _create_postgres_engine_from_url

        url = "postgresql://user@localhost/db"
        engine = _create_postgres_engine_from_url(url)

        assert engine.config["port"] == 5432  # Default port

    def test_app_registry(self):
        """Test APP_REGISTRY is properly configured."""
        from piccolo_conf import APP_REGISTRY

        assert "llm_tracer.db.piccolo_app" in APP_REGISTRY.apps
