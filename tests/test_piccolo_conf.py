"""Tests for Piccolo and database configuration."""

import os
from unittest.mock import patch

from piccolo.engine.sqlite import SQLiteEngine

from llm_tracer.config import Settings


class TestDatabaseConfig:
    """Tests for database configuration."""

    def test_default_sqlite_url(self):
        """Test default database URL is SQLite."""
        with patch.dict(os.environ, {}, clear=True):
            s = Settings()
            assert s.DATABASE_URL.startswith("sqlite")

    def test_database_url_from_env(self):
        """Test DATABASE_URL from environment."""
        with patch.dict(
            os.environ, {"DATABASE_URL": "postgresql://user:pass@localhost:5432/testdb"}, clear=True
        ):
            s = Settings()
            assert s.DATABASE_URL == "postgresql://user:pass@localhost:5432/testdb"

    def test_get_database_url_prefers_explicit(self):
        """Test get_database_url prefers DATABASE_URL."""
        with patch.dict(
            os.environ,
            {
                "DATABASE_URL": "postgresql://user:pass@localhost:5432/testdb",
                "POSTGRES_HOST": "otherhost",
            },
            clear=True,
        ):
            s = Settings()
            url = s.get_database_url()
            assert "user:pass@localhost" in url

    def test_get_database_url_from_postgres_vars(self):
        """Test get_database_url builds URL from POSTGRES_* vars."""
        with patch.dict(
            os.environ,
            {
                "POSTGRES_HOST": "myhost",
                "POSTGRES_PORT": "5433",
                "POSTGRES_USER": "myuser",
                "POSTGRES_PASSWORD": "mypass",
                "POSTGRES_DB": "mydb",
            },
            clear=True,
        ):
            s = Settings()
            url = s.get_database_url()
            assert "myuser:mypass@myhost:5433/mydb" in url

    def test_default_settings(self):
        """Test default settings values."""
        with patch.dict(os.environ, {}, clear=True):
            s = Settings()
            assert s.HOST == "0.0.0.0"
            assert s.PORT == 8000
            assert s.DEBUG is False
            assert s.APP_NAME == "LLM Tracer"
