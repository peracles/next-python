# backend/app/modules/users/models.py
"""
Modelos de base de datos para el módulo de usuarios

SQLAlchemy usa clases de Python para representar tablas.
Cada atributo de la clase es una columna en la tabla.
"""

from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey
from sqlalchemy.sql import func  # ← Para funciones SQL como NOW()
from sqlalchemy.orm import relationship  # ← Para relaciones entre tablas
from app.core.database import Base  # ← Clase base de la que heredan todos los modelos


class User(Base):
    """
    Modelo de usuario en la base de datos
    
    Esta clase representa la tabla 'users' en PostgreSQL.
    
    Equivalent SQL:
    CREATE TABLE users (
        id SERIAL PRIMARY KEY,
        email VARCHAR UNIQUE NOT NULL,
        username VARCHAR UNIQUE NOT NULL,
        hashed_password VARCHAR NOT NULL,
        is_active BOOLEAN DEFAULT TRUE,
        is_superuser BOOLEAN DEFAULT FALSE,
        created_at TIMESTAMP DEFAULT NOW(),
        updated_at TIMESTAMP
    );
    """
    
    # Nombre de la tabla en la base de datos
    __tablename__ = "users"
    __table_args__ = {"schema": "auth"}
    
    # ─────────────────────────────────────────────────────────
    # Columnas de la tabla
    # ─────────────────────────────────────────────────────────
    
    # Columna: id (llave primaria, autoincremental)
    id = Column(
        Integer, 
        primary_key=True,      # ← Llave primaria (única, no nula)
        index=True             # ← Crea un índice para búsquedas más rápidas
    )
    
    # Columna: email (único, requerido, indexado)
    email = Column(
        String, 
        unique=True,           # ← No puede haber dos usuarios con el mismo email
        index=True,            # ← Índice para búsquedas por email
        nullable=False         # ← No puede ser NULL (requerido)
    )
    
    # Columna: username (único, requerido, indexado)
    username = Column(
        String, 
        unique=True, 
        index=True, 
        nullable=False
    )
    
    # Columna: hashed_password (requerido, NO guardar password en texto plano)
    hashed_password = Column(
        String, 
        nullable=False
    )
    
    # Columna: is_active (por defecto True)
    is_active = Column(
        Boolean, 
        default=True           # ← Valor por defecto si no se especifica
    )
    
    # Columna: is_superuser (por defecto False)
    is_superuser = Column(
        Boolean, 
        default=False
    )
    
    # Columna: created_at (timestamp automático al crear)
    created_at = Column(
        DateTime(timezone=True), 
        server_default=func.now()  # ← NOW() de SQL, se ejecuta en la DB
    )
    
    # Columna: updated_at (timestamp automático al actualizar)
    updated_at = Column(
        DateTime(timezone=True), 
        onupdate=func.now()    # ← Se actualiza automáticamente al hacer UPDATE
    )
    
    # ─────────────────────────────────────────────────────────
    # Relaciones con otras tablas (opcional, para Issue #4)
    # ─────────────────────────────────────────────────────────
    # Ejemplo: Un usuario puede tener muchos posts
    # posts = relationship("Post", back_populates="user")
    
    # ─────────────────────────────────────────────────────────
    # Método para representación en string (útil para debug)
    # ─────────────────────────────────────────────────────────
    def __repr__(self) -> str:
        """
        Retorna una representación en string del objeto
        
        Útil para debug en consola:
        >>> user = User(email="test@example.com")
        >>> print(user)
        <User(id=None, email='test@example.com')>
        """
        return f"<User(id={self.id}, email='{self.email}')>"