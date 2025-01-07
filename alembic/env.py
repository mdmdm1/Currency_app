from logging.config import fileConfig
from database.models import Base
from sqlalchemy import create_engine, pool
from alembic import context
import os

# Set Oracle environment variables
os.environ["NLS_LANG"] = ".AL32UTF8"
os.environ["NLS_NCHAR"] = "AL16UTF16"

# this is the Alembic Config object
config = context.config

# Interpret the config file for Python logging
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# add your model's MetaData object here
target_metadata = Base.metadata

# Database URL
DATABASE_URL = "oracle+cx_oracle://admin:2024@localhost:1521/?service_name=MANAGEMENT4"


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode."""
    context.configure(
        url=DATABASE_URL,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={
            "paramstyle": "named",
            "encoding": "UTF-8",
            "nencoding": "UTF-16",
        },
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode."""
    engine_args = {
        "poolclass": pool.NullPool,
        "connect_args": {
            "encoding": "UTF-8",
            "nencoding": "UTF-16",
            "events": True,
            "threaded": True,
        },
    }

    connectable = create_engine(DATABASE_URL, **engine_args)

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            compare_type=True,
            compare_server_default=True,
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
