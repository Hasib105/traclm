"""Piccolo ORM app configuration."""

import os

from piccolo.conf.apps import AppConfig

from llm_tracer.db.models import APIKey, LLMTrace, Project, User

CURRENT_DIRECTORY = os.path.dirname(os.path.abspath(__file__))

APP_CONFIG = AppConfig(
    app_name="llm_tracer",
    migrations_folder_path=os.path.join(CURRENT_DIRECTORY, "migrations"),
    table_classes=[User, Project, APIKey, LLMTrace],
)
