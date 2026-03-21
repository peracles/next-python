# backend/tests/conftest.py
"""
Fixtures globales para pytest

Este archivo se ejecuta automáticamente antes de los tests.
Define recursos compartidos como:
- Base de datos de tests (SQLite en memoria)
- Cliente HTTP para hacer requests a la API
- Usuarios de prueba
"""

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker

from app.main import app
from app.core.database import Base, get_db


# ─────────────────────────────────────────────────────────────
# Configuración de base de datos para tests
# ─────────────────────────────────────────────────────────────
# Usamos SQLite en memoria para tests: rápido y aislado
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"

# Engine y session maker para tests
test_engine = create_async_engine(TEST_DATABASE_URL, echo=False)
test_session_maker = async_sessionmaker(
    test_engine,
    class_=AsyncSession,
    expire_on_commit=False
)


# ─────────────────────────────────────────────────────────────
# Fixture: Sesión de base de datos para cada test
# ─────────────────────────────────────────────────────────────
@pytest.fixture(scope="function")
async def db_session():
    """
    Fixture que provee una sesión de DB limpia para cada test
    
    scope="function" = nueva sesión para cada función de test
    
    Flujo:
    1. Antes del test: crear tablas vacías
    2. Durante el test: usar la sesión para queries
    3. Después del test: eliminar tablas (limpieza)
    """
    # Crear todas las tablas en la DB de tests
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    # Crear sesión para el test
    async with test_session_maker() as session:
        yield session  # ← El test usa esta sesión
    
    # Limpiar después del test
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


# ─────────────────────────────────────────────────────────────
# Fixture: Cliente HTTP para hacer requests a la API
# ─────────────────────────────────────────────────────────────
@pytest.fixture(scope="function")
async def client(db_session):
    """
    Fixture que provee un cliente HTTP para tests de API
    
    Override de la dependencia get_db para usar la DB de tests
    en lugar de la DB real.
    
    Uso en tests:
    async def test_get_users(client: AsyncClient):
        response = await client.get("/users")
        assert response.status_code == 200
    """
    # Override de get_db: en lugar de la DB real, usa la de tests
    async def override_get_db():
        yield db_session
    
    app.dependency_overrides[get_db] = override_get_db
    
    # Crear cliente HTTP asíncrono
    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac  # ← El test usa este cliente
    
    # Limpiar overrides después del test
    app.dependency_overrides.clear()


# ─────────────────────────────────────────────────────────────
# Fixture: Usuario de prueba (opcional, para tests de auth)
# ─────────────────────────────────────────────────────────────
@pytest.fixture
def test_user_data():
    """Datos de un usuario de prueba"""
    return {
        "email": "test@example.com",
        "username": "testuser",
        "password": "TestPassword123!"
    }