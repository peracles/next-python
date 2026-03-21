# backend/app/modules/users/schemas.py
"""
Esquemas de validación para el módulo de usuarios

Pydantic valida y transforma datos automáticamente:
- Request: valida que el cliente envíe datos correctos
- Response: asegura que la API devuelva datos con la estructura esperada

Esto genera documentación automática en Swagger UI.
"""

from pydantic import BaseModel, EmailStr, ConfigDict, Field
from datetime import datetime
from typing import Optional


# ─────────────────────────────────────────────────────────────
# Schema para CREAR usuario (lo que el cliente envía en POST /users)
# ─────────────────────────────────────────────────────────────
class UserCreate(BaseModel):
    """
    Datos necesarios para crear un nuevo usuario
    
    Se usa en: POST /users
    
    Validaciones automáticas de Pydantic:
    - email: debe ser un email válido (formato user@domain.com)
    - username: debe tener entre 3 y 50 caracteres
    - password: debe tener al menos 8 caracteres
    """
    
    email: EmailStr = Field(
        ...,  # ← ... significa "requerido" (no puede ser None)
        description="Email único del usuario",
        examples=["usuario@ejemplo.com"]
    )
    
    username: str = Field(
        ...,
        min_length=3,
        max_length=50,
        description="Nombre de usuario único (3-50 caracteres)",
        examples=["juanperez"]
    )
    
    password: str = Field(
        ...,
        min_length=8,
        description="Contraseña (mínimo 8 caracteres)",
        examples=["secret123"]
    )
    
    # Configuración opcional de Pydantic
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "email": "usuario@ejemplo.com",
                "username": "juanperez",
                "password": "secret123"
            }
        }
    )


# ─────────────────────────────────────────────────────────────
# Schema para ACTUALIZAR usuario (datos opcionales en PUT /users/{id})
# ─────────────────────────────────────────────────────────────
class UserUpdate(BaseModel):
    """
    Datos opcionales para actualizar un usuario existente
    
    Se usa en: PUT /users/{id}
    
    Todos los campos son opcionales (None por defecto).
    Solo se actualizan los campos que el cliente envíe.
    """
    
    email: Optional[EmailStr] = Field(
        None,
        description="Nuevo email del usuario (opcional)"
    )
    
    username: Optional[str] = Field(
        None,
        min_length=3,
        max_length=50,
        description="Nuevo nombre de usuario (opcional)"
    )
    
    password: Optional[str] = Field(
        None,
        min_length=8,
        description="Nueva contraseña (opcional)"
    )
    
    is_active: Optional[bool] = Field(
        None,
        description="Estado de la cuenta (activo/inactivo)"
    )


# ─────────────────────────────────────────────────────────────
# Schema para RESPUESTA (lo que la API devuelve al cliente)
# ─────────────────────────────────────────────────────────────
class UserResponse(BaseModel):
    """
    Datos que se devuelven al cliente después de operaciones con usuarios
    
    Se usa en: GET /users, GET /users/{id}, POST /users, PUT /users/{id}
    
    Nota importante: NO incluye password por seguridad.
    """
    
    id: int = Field(
        description="ID único del usuario"
    )
    
    email: EmailStr = Field(
        description="Email del usuario"
    )
    
    username: str = Field(
        description="Nombre de usuario"
    )
    
    is_active: bool = Field(
        description="¿La cuenta está activa?"
    )
    
    is_superuser: bool = Field(
        description="¿El usuario es administrador?"
    )
    
    created_at: datetime = Field(
        description="Fecha y hora de creación"
    )
    
    updated_at: Optional[datetime] = Field(
        None,
        description="Fecha y hora de última actualización"
    )
    
    # Configuración crítica: from_attributes=True
    model_config = ConfigDict(
        from_attributes=True  # ← Permite convertir objetos SQLAlchemy a Pydantic
    )


# ─────────────────────────────────────────────────────────────
# Schema para Login (lo que el cliente envía en POST /auth/login)
# ─────────────────────────────────────────────────────────────
class UserLogin(BaseModel):
    """
    Datos para autenticar un usuario
    
    Se usa en: POST /auth/login
    """
    
    email: EmailStr = Field(
        ...,
        description="Email del usuario",
        examples=["usuario@ejemplo.com"]
    )
    
    password: str = Field(
        ...,
        description="Contraseña del usuario",
        examples=["secret123"]
    )


# ─────────────────────────────────────────────────────────────
# Schema para Token JWT (lo que la API devuelve después de login)
# ─────────────────────────────────────────────────────────────
class Token(BaseModel):
    """
    Token de acceso JWT
    
    Se devuelve después de un login exitoso.
    """
    
    access_token: str = Field(
        description="Token JWT para autenticar requests futuros"
    )
    
    token_type: str = Field(
        default="bearer",
        description="Tipo de token (siempre 'bearer' para OAuth2)"
    )


# ─────────────────────────────────────────────────────────────
# Schema para Token con datos del usuario (respuesta completa de login)
# ─────────────────────────────────────────────────────────────
class TokenData(BaseModel):
    """
    Token JWT + datos del usuario autenticado
    
    Respuesta completa de POST /auth/login
    """
    
    access_token: str
    token_type: str
    user: UserResponse  # ← Incluye los datos del usuario (sin password)