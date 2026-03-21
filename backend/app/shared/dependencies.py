# backend/app/shared/dependencies.py
"""
Dependencias compartidas entre módulos

Aquí van funciones que se reusan en múltiples partes de la app:
- get_db: Sesión de base de datos (ya definida en core/database.py)
- get_current_user: Usuario autenticado (ya definida en auth/service.py)
- get_current_active_user: Usuario activo (variante de get_current_user)
- get_current_superuser: Usuario administrador

Estas funciones se importan en los routers con Depends().
"""

from fastapi import Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.modules.auth.service import get_current_user
from app.modules.users.schemas import UserResponse


async def get_current_active_user(
    current_user: UserResponse = Depends(get_current_user)
) -> UserResponse:
    """
    Dependency que verifica que el usuario autenticado esté activo
    
    Se usa para proteger endpoints que requieren cuenta activa:
    
    @app.get("/dashboard")
    async def dashboard(current_user: User = Depends(get_current_active_user)):
        # Solo usuarios activos llegan aquí
        return {"message": f"Bienvenido, {current_user.username}"}
    
    Args:
        current_user: Usuario autenticado (de get_current_user)
    
    Returns:
        UserResponse: Mismo usuario si está activo
    
    Raises:
        HTTPException 400: Si el usuario existe pero está inactivo
    """
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cuenta inactiva"
        )
    return current_user


async def get_current_superuser(
    current_user: UserResponse = Depends(get_current_active_user)
) -> UserResponse:
    """
    Dependency que verifica que el usuario sea administrador
    
    Se usa para proteger endpoints de administración:
    
    @app.delete("/users/{id}")
    async def delete_user(current_user: User = Depends(get_current_superuser)):
        # Solo superusers pueden eliminar usuarios
        pass
    
    Args:
        current_user: Usuario activo (de get_current_active_user)
    
    Returns:
        UserResponse: Mismo usuario si es superuser
    
    Raises:
        HTTPException 403: Si el usuario no es administrador
    """
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permisos de administrador"
        )
    return current_user