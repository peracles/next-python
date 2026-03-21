# backend/app/core/config.py
"""
Configuración central de la aplicación

Usa Pydantic Settings para leer variables de entorno automáticamente.
Todo lo que necesites configurar va aquí.
"""

from pydantic_settings import BaseSettings
from functools import lru_cache
from typing import Optional


class Settings(BaseSettings):
    """
    Esquema de configuración de la aplicación
    
    Cada atributo representa:
    - Una variable de entorno (si existe)
    - O un valor por defecto (si no existe)
    
    Pydantic valida automáticamente:
    - Tipos de datos (str, int, bool, etc.)
    - Valores requeridos vs opcionales
    - Formatos especiales (emails, URLs, etc.)
    """
    
    # ─────────────────────────────────────────────────────────
    # App Metadata (Información básica de la API)
    # ─────────────────────────────────────────────────────────
    APP_NAME: str = "Next-Python API"
    APP_VERSION: str = "1.0.0"
    ENVIRONMENT: str = "development"  # development, staging, production
    
    # ─────────────────────────────────────────────────────────
    # Database Configuration (Conexión a PostgreSQL)
    # ─────────────────────────────────────────────────────────
    DB_USER: str = "admin"
    DB_PASSWORD: str = "nextpythonDBPassword2026"
    DB_NAME: str = "next_python_db"
    DB_HOST: str = "next-python_db"  # ← Nombre del servicio en Docker Compose
    DB_PORT: int = 5432
    
    # ─────────────────────────────────────────────────────────
    # JWT / Authentication (Configuración de tokens)
    # ─────────────────────────────────────────────────────────
    JWT_SECRET_KEY: str = "change-me-in-production-use-a-long-random-string"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # ─────────────────────────────────────────────────────────
    # Testing (Configuración específica para tests)
    # ─────────────────────────────────────────────────────────
    TEST_DATABASE_URL: Optional[str] = None
    
    # ─────────────────────────────────────────────────────────
    # Propiedades calculadas (no se leen de .env, se calculan)
    # ─────────────────────────────────────────────────────────
    @property
    def database_url(self) -> str:
        """
        Construye la URL de conexión a PostgreSQL
        
        Formato SQLAlchemy: postgresql+asyncpg://user:pass@host:port/dbname
        
        Si TEST_DATABASE_URL está definido, lo usa (para tests con SQLite en memoria).
        """
        if self.TEST_DATABASE_URL:
            return self.TEST_DATABASE_URL
        
        return (
            f"postgresql+asyncpg://{self.DB_USER}:{self.DB_PASSWORD}"
            f"@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"
        )
    
    # ─────────────────────────────────────────────────────────
    # Configuración interna de Pydantic (no modificar)
    # ─────────────────────────────────────────────────────────
    class Config:
        env_file = ".env"              # ← Lee variables desde archivo .env en la raíz
        case_sensitive = True          # ← Las variables distinguen mayúsculas/minúsculas


# ─────────────────────────────────────────────────────────────
# Instancia global de configuración (singleton con caché)
# ─────────────────────────────────────────────────────────────
@lru_cache()
def get_settings() -> Settings:
    """
    Retorna una instancia cached de Settings
    
    ¿Por qué @lru_cache?
    - La primera vez que se llama, lee .env y crea el objeto Settings
    - Las siguientes veces, retorna el mismo objeto sin volver a leer .env
    - Es más eficiente y asegura consistencia en toda la app
    """
    return Settings()


# Instancia global para usar en TODA la aplicación
# Importa así: from app.core.config import settings
settings = get_settings()