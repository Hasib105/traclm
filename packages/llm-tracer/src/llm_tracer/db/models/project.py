"""Project model for organizing traces."""

from datetime import datetime

from piccolo.columns import ForeignKey, Text, Timestamp, Varchar
from piccolo.table import Table

from llm_tracer.db.models.user import User


class Project(Table):
    """A project that groups traces together."""

    name = Varchar(length=255, unique=True)
    description = Text(null=True)
    owner = ForeignKey(references=User, null=True)
    created_at = Timestamp(default=datetime.now)
    updated_at = Timestamp(default=datetime.now, auto_update=datetime.now)
