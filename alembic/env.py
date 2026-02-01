"""
Alembic env.py configuration.
Menggunakan sync driver untuk migrations.
"""

from logging.config import fileConfig

from sqlalchemy import pool
from sqlalchemy import create_engine

from alembic import context

# Import config dari aplikasi
from app.core.config import settings

# Import semua models agar terdeteksi oleh Alembic
from app.db.session import Base
from app.models import History, Playlist, SongSaved, User  # noqa: F401

# Alembic Config object
config = context.config

# Override sqlalchemy.url dengan URL dari settings
# Konversi asyncpg ke psycopg2 untuk sync migrations
sync_url = settings.database_url.replace("+asyncpg", "")
config.set_main_option("sqlalchemy.url", sync_url)

# Setup loggers dari config file
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# MetaData untuk autogenerate support
target_metadata = Base.metadata


def run_migrations_offline() -> None:
    """
    Run migrations dalam 'offline' mode.
    Hanya generate SQL tanpa koneksi ke database.
    """
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        compare_type=True,
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """
    Run migrations dalam 'online' mode menggunakan sync engine.
    """
    connectable = create_engine(
        config.get_main_option("sqlalchemy.url"),
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            compare_type=True,
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
