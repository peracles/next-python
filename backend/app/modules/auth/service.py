# backend/app/modules/auth/service.py
"""
Lógica de negocio para autenticación con JWT

Funciones principales:
- authenticate_user: Verifica email y password
- create_access_token: Genera token JWT firmado
- get_current_user: Dependency para proteger endpoints
"""

from datetime import datetime, timedelta, timezone
from typing import Optional
from jose import jwt, JWTError  # ← Librería para JWT
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.database import get_db
from app.modules.users.service import get_user_by_email, verify_password
from app.modules.users.schemas import UserResponse

# ─────────────────────────────────────────────────────────────
# Configuración de OAuth2 para FastAPI
# ─────────────────────────────────────────────────────────────
# OAuth2PasswordBearer configura de dónde leer el token
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

# ─────────────────────────────────────────────────────────────
# Función: Autenticar usuario (verificar credenciales)
# ─────────────────────────────────────────────────────────────
async def authenticate_user(
    db: AsyncSession, 
    email: str, 
    password: str
) -> Optional[UserResponse]:
    """
    Verificar si un email y password son válidos
    
    Args:
        db: Sesión de base de datos
        email: Email del usuario
        password: Password en texto plano
    
    Returns:
        UserResponse: Datos del usuario si autenticación exitosa, None si falla
    """
    # Buscar usuario por email
    user = await get_user_by_email(db=db, email=email)
    if not user:
        return None
    
    # Verificar password (compara texto plano con hash)
    if not verify_password(password, user.hashed_password):
        return None
    
    # Retornar datos del usuario (sin password)
    return UserResponse.model_validate(user)  # ← Convierte SQLAlchemy a Pydantic

# ─────────────────────────────────────────────────────────────
# Función: Crear token JWT
# ─────────────────────────────────────────────────────────────
def create_access_token(
    data: dict, 
    expires_delta: Optional[timedelta] = None
) -> str:
    """
    Crear un token JWT firmado
    
    Args:
        data: Diccionario con datos a incluir en el token (ej: {"sub": "email"})
        expires_delta: Duración del token (default: 15 minutos)
    
    Returns:
        str: Token JWT codificado como string
    """
    # Copiar datos para no modificar el original
    to_encode = data.copy()
    
    # Calcular fecha de expiración
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=15)
    
    # Agregar claims estándar de JWT
    to_encode.update({"exp": expire})  # ← exp: expiration time
    
    # Codificar y firmar el token
    encoded_jwt = jwt.encode(
        to_encode, 
        settings.JWT_SECRET_KEY, 
        algorithm=settings.JWT_ALGORITHM
    )
    
    return encoded_jwt

# ─────────────────────────────────────────────────────────────
# Dependency: Obtener usuario actual desde token JWT
# ─────────────────────────────────────────────────────────────
async def get_current_user(
    token: str = Depends(oauth2_scheme),  # ← Extrae token de header Authorization
    db: AsyncSession = Depends(get_db)
) -> UserResponse:
    """
    Dependency para proteger endpoints: verifica token y retorna usuario
    
    Se usa así en un endpoint:
    @app.get("/protected")
    async def protected_route(current_user: User = Depends(get_current_user)):
        # current_user ya está autenticado
        return {"message": f"Hola, {current_user.username}"}
    
    Args:
        token: Token JWT extraído del header Authorization: Bearer <token>
        db: Sesión de base de datos
    
    Returns:
        UserResponse: Datos del usuario autenticado
    
    Raises:
        HTTPException 401: Si el token es inválido o expirado
        HTTPException 404: Si el usuario del token no existe
    """
    # CredentialsException es un HTTP 401 estándar para OAuth2
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Credenciales inválidas",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        # Decodificar y verificar el token
        payload = jwt.decode(
            token, 
            settings.JWT_SECRET_KEY, 
            algorithms=[settings.JWT_ALGORITHM]
        )
        
        # Extraer el email del campo "sub" (subject) del token
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
            
    except JWTError:
        # Si hay error al decodificar (token inválido, expirado, firma incorrecta)
        raise credentials_exception
    
    # Buscar usuario en la base de datos
    user = await get_user_by_email(db=db, email=email)
    if user is None:
        raise credentials_exception
    
    # Retornar datos del usuario (sin password)
    return UserResponse.model_validate(user)