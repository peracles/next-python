# backend/app/modules/auth/router.py
"""
Router para el módulo de autenticación

Define los endpoints para:
- POST /auth/login - Autenticar usuario y obtener token JWT
- POST /auth/register - Registrar nuevo usuario (opcional)
- POST /auth/logout - Invalidar token (opcional, requiere blacklist)

Autenticación con JWT (JSON Web Tokens):
1. Usuario envía email + password
2. Servidor verifica credenciales
3. Si son válidas, genera un token JWT firmado con JWT_SECRET_KEY
4. Cliente incluye el token en header "Authorization: Bearer <token>" en requests futuros
5. Servidor verifica la firma del token para autenticar al usuario
"""

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm  # ← Formulario estándar OAuth2
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import timedelta

from app.core.config import settings
from app.core.database import get_db
from app.modules.auth.schemas import UserLogin, Token, TokenData
from app.modules.auth.service import (
    authenticate_user,
    create_access_token,
    get_current_user  # ← Dependency para proteger endpoints
)
from app.modules.users.schemas import UserResponse, UserCreate

# ─────────────────────────────────────────────────────────────
# 1. Crear instancia de APIRouter
# ─────────────────────────────────────────────────────────────
router = APIRouter(
    prefix="/auth",  # ← Todas las rutas empiezan con /auth
    tags=["auth"]    # ← Agrupa en Swagger bajo etiqueta "auth"
)

# ─────────────────────────────────────────────────────────────
# 2. Endpoint: POST /auth/login - Autenticar usuario
# ─────────────────────────────────────────────────────────────
@router.post("/login", response_model=Token)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),  # ← Parsea form-data estándar OAuth2
    db: AsyncSession = Depends(get_db)
):
    """
    Autenticar usuario y obtener token de acceso JWT
    
    Request (form-data, application/x-www-form-urlencoded):
    - username: Email del usuario (OAuth2 usa "username" para email)
    - password: Contraseña del usuario
    
    Retorna:
    - Token: {access_token: "jwt_string", token_type: "bearer"}
    - HTTP 401 si las credenciales son inválidas
    
    Ejemplo con curl:
    curl -X POST http://localhost:8000/auth/login \
      -d "username=usuario@ejemplo.com" \
      -d "password=secret123"
    
    Ejemplo con JavaScript fetch:
    const response = await fetch('/auth/login', {
      method: 'POST',
      headers: {'Content-Type': 'application/x-www-form-urlencoded'},
      body: new URLSearchParams({
        username: 'usuario@ejemplo.com',
        password: 'secret123'
      })
    })
    """
    # Autenticar usuario (verifica email y password)
    user = await authenticate_user(
        db=db,
        email=form_data.username,  # ← OAuth2 usa "username" para email
        password=form_data.password
    )
    
    # Si la autenticación falla, lanzar error 401
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email o contraseña incorrectos",
            headers={"WWW-Authenticate": "Bearer"},  # ← Para que Swagger muestre el auth
        )
    
    # Crear token JWT con duración configurada
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.email},  # ← "sub" es el subject del token (estándar JWT)
        expires_delta=access_token_expires
    )
    
    return Token(access_token=access_token, token_type="bearer")

# ─────────────────────────────────────────────────────────────
# 3. Endpoint: GET /auth/me - Obtener datos del usuario actual
# ─────────────────────────────────────────────────────────────
@router.get("/me", response_model=UserResponse)
async def read_users_me(
    current_user: UserResponse = Depends(get_current_user)  # ← Dependency que verifica token
):
    """
    Obtener datos del usuario autenticado
    
    Requiere:
    - Header: Authorization: Bearer <token_jwt>
    
    Retorna:
    - UserResponse con datos del usuario (sin password)
    
    Ejemplo con curl:
    curl -H "Authorization: Bearer <token_jwt>" \
      http://localhost:8000/auth/me
    """
    return current_user

# ─────────────────────────────────────────────────────────────
# 4. Endpoint: POST /auth/register - Registrar nuevo usuario (opcional)
# ─────────────────────────────────────────────────────────────
@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(
    user_data: UserCreate,  # ← Reusamos el schema de creación de users
    db: AsyncSession = Depends(get_db)
):
    """
    Registrar un nuevo usuario (alternativa a POST /users si quieres auth separada)
    
    Request body (JSON):
    {
        "email": "nuevo@ejemplo.com",
        "username": "nuevo_usuario",
        "password": "password_seguro"
    }
    
    Retorna:
    - UserResponse con datos del usuario creado
    """
    # Reusamos la lógica de creación de users
    # En una implementación real, aquí llamarías a create_user del service de users
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Registro de usuarios se maneja en POST /users"
    )