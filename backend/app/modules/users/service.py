# backend/app/modules/users/service.py
"""
Lógica de negocio para el módulo de usuarios

Los servicios contienen la lógica que no debería estar en los routers:
- Consultas complejas a la base de datos
- Reglas de negocio
- Transformación de datos
- Integración con servicios externos

Los routers solo deberían:
- Validar requests (Pydantic)
- Llamar al servicio apropiado
- Retornar responses
"""

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete
from passlib.context import CryptContext  # ← Para hashear passwords
from app.modules.users.models import User
from app.modules.users.schemas import UserCreate, UserUpdate
from typing import Optional, List


# ─────────────────────────────────────────────────────────────
# Configuración de hashing de passwords
# ─────────────────────────────────────────────────────────────
# pwd_context configura el algoritmo de hashing (bcrypt por defecto)
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verificar si una contraseña en texto plano coincide con un hash
    
    Se usa en login para comparar la password ingresada con la guardada.
    
    Args:
        plain_password: Contraseña en texto plano (la que ingresa el usuario)
        hashed_password: Hash almacenado en la base de datos
    
    Returns:
        bool: True si coinciden, False si no
    """
    return pwd_context.verify(plain_password, hashed_password)

def hash_password(password: str) -> str:
    """
    Hashear una contraseña antes de guardarla en la base de datos
    
    NUNCA guardar passwords en texto plano.
    
    Args:
        password: Contraseña en texto plano
    
    Returns:
        str: Hash de la contraseña (bcrypt)
    """
    return pwd_context.hash(password)

# ─────────────────────────────────────────────────────────────
# Funciones de consulta (READ)
# ─────────────────────────────────────────────────────────────
async def get_user_by_id(db: AsyncSession, user_id: int) -> Optional[User]:
    """
    Obtener un usuario por su ID
    
    Args:
        db: Sesión de base de datos
        user_id: ID del usuario a buscar
    
    Returns:
        User: Objeto User si existe, None si no
    """
    # SQLAlchemy query: SELECT * FROM users WHERE id = :user_id
    result = await db.execute(select(User).where(User.id == user_id))
    return result.scalar_one_or_none()  # ← Retorna None si no encuentra

async def get_user_by_email(db: AsyncSession, email: str) -> Optional[User]:
    """
    Obtener un usuario por su email
    
    Args:
        db: Sesión de base de datos
        email: Email del usuario a buscar
    
    Returns:
        User: Objeto User si existe, None si no
    """
    result = await db.execute(select(User).where(User.email == email))
    return result.scalar_one_or_none()

async def get_user_by_username(db: AsyncSession, username: str) -> Optional[User]:
    """
    Obtener un usuario por su username
    
    Args:
        db: Sesión de base de datos
        username: Username del usuario a buscar
    
    Returns:
        User: Objeto User si existe, None si no
    """
    result = await db.execute(select(User).where(User.username == username))
    return result.scalar_one_or_none()

async def get_users(
    db: AsyncSession, 
    skip: int = 0, 
    limit: int = 100
) -> List[User]:
    """
    Obtener lista de usuarios con paginación
    
    Args:
        db: Sesión de base de datos
        skip: Número de registros a saltar (offset)
        limit: Máximo de registros a retornar
    
    Returns:
        List[User]: Lista de objetos User
    """
    # SQLAlchemy query: SELECT * FROM users LIMIT :limit OFFSET :skip
    result = await db.execute(
        select(User)
        .offset(skip)
        .limit(limit)
    )
    return result.scalars().all()  # ← .all() retorna lista de objetos

# ─────────────────────────────────────────────────────────────
# Funciones de creación (CREATE)
# ─────────────────────────────────────────────────────────────
async def create_user(
    db: AsyncSession,
    email: str,
    username: str,
    hashed_password: str,
    is_superuser: bool = False
) -> User:
    """
    Crear un nuevo usuario en la base de datos
    
    Args:
        db: Sesión de base de datos
        email: Email del usuario (ya validado como único)
        username: Username del usuario (ya validado como único)
        hashed_password: Password ya hasheada (usar hash_password())
        is_superuser: Si el usuario es administrador (default: False)
    
    Returns:
        User: Objeto User creado con ID asignado
    """
    # Crear instancia del modelo User
    db_user = User(
        email=email,
        username=username,
        hashed_password=hashed_password,
        is_superuser=is_superuser
    )
    
    # Agregar a la sesión y hacer commit
    db.add(db_user)
    await db.commit()
    await db.refresh(db_user)  # ← Recarga el objeto con datos de la DB (como el ID)
    
    return db_user

# ─────────────────────────────────────────────────────────────
# Funciones de actualización (UPDATE)
# ─────────────────────────────────────────────────────────────
async def update_user(
    db: AsyncSession,
    user: User,
    update_data: UserUpdate
) -> User:
    """
    Actualizar los datos de un usuario existente
    
    Args:
        db: Sesión de base de datos
        user: Objeto User existente a actualizar
        update_data: Datos a actualizar (solo los campos no-None se aplican)
    
    Returns:
        User: Objeto User actualizado
    """
    # Actualizar solo los campos que no sean None
    update_data_dict = update_data.model_dump(exclude_unset=True)
    
    for key, value in update_data_dict.items():
        if value is not None:
            setattr(user, key, value)  # ← user.email = nuevo_valor, etc.
    
    # Hacer commit para guardar cambios
    await db.commit()
    await db.refresh(user)
    
    return user

# ─────────────────────────────────────────────────────────────
# Funciones de eliminación (DELETE)
# ─────────────────────────────────────────────────────────────
async def delete_user(db: AsyncSession, user: User) -> None:
    """
    Eliminar un usuario de la base de datos
    
    Args:
        db: Sesión de base de datos
        user: Objeto User a eliminar
    
    Returns:
        None
    """
    await db.delete(user)
    await db.commit()