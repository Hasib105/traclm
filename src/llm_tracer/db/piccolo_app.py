"""Piccolo app configuration."""

from pathlib import Path

from piccolo.conf.apps import AppConfig

CURRENT_DIRECTORY = Path(__file__).resolve().parent

APP_CONFIG = AppConfig(
    app_name="llm_tracer",
    migrations_folder_path=str(CURRENT_DIRECTORY / "migrations"),
    table_classes=[],
    migration_dependencies=[],
    commands=[],
)
