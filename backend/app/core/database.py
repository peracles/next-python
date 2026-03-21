# backend/app/core/database.py
"""
Configuración de conexión a base de datos con SQLAlchemy Async

SQLAlchemy es un ORM (Object-Relational Mapper) que te permite:
- Escribir queries en Python en lugar de SQL puro
- Trabajar con objetos en lugar de diccionarios
- Cambiar de base de datos sin reescribir código

Async significa que las operaciones de DB no bloquean el servidor.
"""

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase
from app.core.config import settings


# ─────────────────────────────────────────────────────────────
# 1. Engine: Motor de conexión a la base de datos
# ─────────────────────────────────────────────────────────────
# create_async_engine crea un pool de conexiones reutilizables
engine = create_async_engine(
    settings.database_url,           # ← URL de conexión (de config.py)
    echo=settings.ENVIRONMENT == "development",  # ← Muestra SQL en consola si es dev
    pool_pre_ping=True,              # ← Verifica que la conexión está viva antes de usarla
    pool_recycle=3600,               # ← Recicla conexiones después de 1 hora
)

# ─────────────────────────────────────────────────────────────
# 2. Session Maker: Fábrica de sesiones de base de datos
# ─────────────────────────────────────────────────────────────
# async_sessionmaker crea sesiones asíncronas para hacer queries
async_session_maker = async_sessionmaker(
    engine,                          # ← El engine creado arriba
    class_=AsyncSession,             # ← Usa sesiones asíncronas
    expire_on_commit=False,          # ← No expirar objetos después de commit (mejor para async)
)

# ─────────────────────────────────────────────────────────────
# 3. Base: Clase base para todos los modelos SQLAlchemy
# ─────────────────────────────────────────────────────────────
class Base(DeclarativeBase):
    """
    Clase base para modelos de base de datos
    
    Todos tus modelos heredarán de esta clase:
    
    Ejemplo:
    class User(Base):
        __tablename__ = "users"
        id = Column(Integer, primary_key=True)
        email = Column(String, unique=True)
        # ... más columnas
    
    Base.metadata.create_all(engine)  # ← Crea las tablas en la DB
    """
    pass

# ─────────────────────────────────────────────────────────────
# 4. Dependency: Función para obtener sesión de DB en endpoints
# ─────────────────────────────────────────────────────────────
async def get_db() -> AsyncSession:
    """
    Dependency de FastAPI que provee una sesión de base de datos
    
    ¿Qué es una Dependency en FastAPI?
    - Es una función que FastAPI ejecuta automáticamente antes de tu endpoint
    - El resultado se "inyecta" como parámetro en tu función
    - Es útil para: conexiones a DB, autenticación, logging, etc.
    
    Se usa en endpoints así:
    
    @app.get("/users")
    async def get_users(db: AsyncSession = Depends(get_db)):
        # usar db para hacer queries
        result = await db.execute(select(User))
        users = result.scalars().all()
        return users
    
    La sesión se cierra automáticamente después del request gracias al yield.
    """
    async with async_session_maker() as session:
        try:
            yield session  # ← Provee la sesión al endpoint
        finally:
            await session.close()  # ← Cierra la sesión después del request

# ─────────────────────────────────────────────────────────────
# 5. Funciones para inicialización de tests (crear/eliminar tablas)
# ─────────────────────────────────────────────────────────────
async def init_db():
    """
    Crear todas las tablas en la base de datos
    
    Solo para tests o inicialización inicial.
    En producción, usa Alembic migrations (Issue #5).
    """
    async with engine.begin() as conn:
        # Base.metadata contiene todos los modelos que heredan de Base
        await conn.run_sync(Base.metadata.create_all)

async def drop_db():
    """
    Eliminar todas las tablas de la base de datos
    
    Solo para tests. Nunca usar en producción.
    """
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)