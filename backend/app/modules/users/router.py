# backend/app/modules/users/router.py
"""
Router para el módulo de usuarios

Define los endpoints HTTP para operaciones CRUD de usuarios:
- GET /users - Listar todos
- GET /users/{id} - Obtener uno
- POST /users - Crear nuevo
- PUT /users/{id} - Actualizar
- DELETE /users/{id} - Eliminar

Cada endpoint usa:
- @router.X() para registrar la ruta
- response_model para validar la respuesta
- Depends() para inyectar dependencias como la sesión de DB
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List

from app.core.database import get_db
from app.modules.users.models import User
from app.modules.users.schemas import UserCreate, UserResponse, UserUpdate
from app.modules.users.service import (
    get_user_by_id,
    get_user_by_email,
    create_user as create_user_service,
    update_user as update_user_service,
    delete_user as delete_user_service,
    hash_password  # ← Para hashear password antes de guardar
)

# ─────────────────────────────────────────────────────────────
# 1. Crear instancia de APIRouter
# ─────────────────────────────────────────────────────────────
router = APIRouter(
    prefix="/users",  # ← Todas las rutas de este router empiezan con /users
    tags=["users"]    # ← Agrupa endpoints en Swagger UI bajo la etiqueta "users"
)

# ─────────────────────────────────────────────────────────────
# 2. Endpoint: GET /users - Listar todos los usuarios
# ─────────────────────────────────────────────────────────────
@router.get("/", response_model=List[UserResponse])
async def get_users(
    skip: int = 0,           # ← Parámetro query: ?skip=10 (paginación)
    limit: int = 100,        # ← Parámetro query: ?limit=50 (máximo a retornar)
    db: AsyncSession = Depends(get_db)  # ← Inyección de sesión de DB
):
    """
    Obtener lista de usuarios con paginación
    
    Parámetros query:
    - skip: Número de registros a saltar (para paginación)
    - limit: Máximo de registros a retornar (default: 100)
    
    Retorna:
    - Lista de objetos UserResponse (sin password)
    
    Ejemplo:
    GET /users?skip=0&limit=10
    """
    # Llamar al servicio para obtener usuarios de la DB
    users = await get_user_by_id(  # ← Esto es un placeholder, ver service.py
        db=db,
        skip=skip,
        limit=limit
    )
    
    return users

# ─────────────────────────────────────────────────────────────
# 3. Endpoint: GET /users/{user_id} - Obtener usuario por ID
# ─────────────────────────────────────────────────────────────
@router.get("/{user_id}", response_model=UserResponse)
async def get_user(
    user_id: int,              # ← Path parameter: /users/123 → user_id=123
    db: AsyncSession = Depends(get_db)
):
    """
    Obtener un usuario específico por su ID
    
    Parámetros path:
    - user_id: ID numérico del usuario
    
    Retorna:
    - UserResponse si existe
    - HTTP 404 si no existe
    
    Ejemplo:
    GET /users/123
    """
    # Llamar al servicio para obtener el usuario
    user = await get_user_by_id(db=db, user_id=user_id)
    
    # Si no se encontró, lanzar error 404
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Usuario con ID {user_id} no encontrado"
        )
    
    return user

# ─────────────────────────────────────────────────────────────
# 4. Endpoint: POST /users - Crear nuevo usuario
# ─────────────────────────────────────────────────────────────
@router.post("/", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def create_user(
    user_data: UserCreate,        # ← Request body validado automáticamente por Pydantic
    db: AsyncSession = Depends(get_db)
):
    """
    Crear un nuevo usuario en el sistema
    
    Request body (JSON):
    {
        "email": "usuario@ejemplo.com",
        "username": "juanperez",
        "password": "secret123"
    }
    
    Validaciones automáticas (Pydantic):
    - email: formato válido
    - username: 3-50 caracteres
    - password: mínimo 8 caracteres
    
    Retorna:
    - UserResponse con datos del usuario creado (sin password)
    - HTTP 201 Created
    
    Ejemplo:
    POST /users
    {
        "email": "nuevo@ejemplo.com",
        "username": "nuevo_usuario",
        "password": "password_seguro_123"
    }
    """
    # Verificar si el email ya está registrado
    existing_user = await get_user_by_email(db=db, email=user_data.email)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email ya registrado"
        )
    
    # Verificar si el username ya está registrado
    existing_username = await get_user_by_id(  # ← Placeholder: implementar búsqueda por username
        db=db, 
        username=user_data.username
    )
    if existing_username:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username ya registrado"
        )
    
    # Hashear password antes de guardar (NUNCA guardar en texto plano)
    hashed_password = hash_password(user_data.password)
    
    # Crear usuario usando el servicio
    new_user = await create_user_service(
        db=db,
        email=user_data.email,
        username=user_data.username,
        hashed_password=hashed_password
    )
    
    return new_user

# ─────────────────────────────────────────────────────────────
# 5. Endpoint: PUT /users/{user_id} - Actualizar usuario
# ─────────────────────────────────────────────────────────────
@router.put("/{user_id}", response_model=UserResponse)
async def update_user(
    user_id: int,
    user_update: UserUpdate,   # ← Datos opcionales a actualizar
    db: AsyncSession = Depends(get_db)
):
    """
    Actualizar los datos de un usuario existente
    
    Request body (JSON) - todos los campos son opcionales:
    {
        "email": "nuevo@email.com",  # ← Opcional
        "username": "nuevo_nombre",   # ← Opcional
        "password": "nueva_password", # ← Opcional (se hashea automáticamente)
        "is_active": false            # ← Opcional
    }
    
    Retorna:
    - UserResponse con datos actualizados
    - HTTP 404 si el usuario no existe
    
    Ejemplo:
    PUT /users/123
    {
        "email": "actualizado@ejemplo.com"
    }
    """
    # Verificar que el usuario existe
    existing_user = await get_user_by_id(db=db, user_id=user_id)
    if not existing_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Usuario con ID {user_id} no encontrado"
        )
    
    # Hashear password si se está actualizando
    if user_update.password:
        user_update.password = hash_password(user_update.password)
    
    # Actualizar usuario usando el servicio
    updated_user = await update_user_service(
        db=db,
        user=existing_user,
        update_data=user_update
    )
    
    return updated_user

# ─────────────────────────────────────────────────────────────
# 6. Endpoint: DELETE /users/{user_id} - Eliminar usuario
# ─────────────────────────────────────────────────────────────
@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(
    user_id: int,
    db: AsyncSession = Depends(get_db)
):
    """
    Eliminar un usuario del sistema
    
    Retorna:
    - HTTP 204 No Content si se eliminó exitosamente
    - HTTP 404 si el usuario no existe
    
    Ejemplo:
    DELETE /users/123
    """
    # Verificar que el usuario existe
    existing_user = await get_user_by_id(db=db, user_id=user_id)
    if not existing_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Usuario con ID {user_id} no encontrado"
        )
    
    # Eliminar usuario usando el servicio
    await delete_user_service(db=db, user=existing_user)
    
    # 204 No Content no retorna body
    return None