# backend/alembic/env.py
from logging.config import fileConfig
from sqlalchemy import pool
from sqlalchemy.ext.asyncio import async_engine_from_config
from alembic import context
import asyncio
import sys
from os.path import abspath, dirname

# Configurar path para importaciones
sys.path.insert(0, dirname(dirname(abspath(__file__))))

from app.core.config import settings
from app.core.database import Base
from app.modules.users.models import User  # noqa

config = context.config
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata

def get_url() -> str:
    return settings.database_url

def run_migrations_offline() -> None:
    url = get_url()
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )
    with context.begin_transaction():
        context.run_migrations()

async def run_migrations_online() -> None:
    """Versión ASÍNCRONA corregida"""
    configuration = config.get_section(config.config_ini_section, {})
    configuration["sqlalchemy.url"] = get_url()
    
    # ✅ Crear engine asíncrono
    connectable = async_engine_from_config(
        configuration,
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )
    
    # ✅ Usar async with para conexión asíncrona
    async with connectable.connect() as connection:
        # ✅ Función wrapper que recibe SOLO la conexión
        def do_migrations(conn):
            context.configure(
                connection=conn,
                target_metadata=target_metadata,
                include_schemas=["auth", "public"]
            )
            context.run_migrations()
        
        # ✅ run_sync pasa automáticamente la conexión
        await connection.run_sync(do_migrations)
        await connection.commit()
    
    await connectable.dispose()

def run_migrations_online_sync() -> None:
    """Wrapper síncrono para Alembic"""
    asyncio.run(run_migrations_online())

if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online_sync()