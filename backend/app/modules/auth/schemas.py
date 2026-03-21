# backend/app/modules/auth/schemas.py
"""
Esquemas de validación para el módulo de autenticación

Ya definimos UserLogin, Token y TokenData en users/schemas.py.
Este archivo puede quedar vacío o importar desde allí:
"""

from app.modules.users.schemas import UserLogin, Token, TokenData

# Si necesitas schemas específicos de auth, agrégalos aquí:
# class RefreshTokenRequest(BaseModel):
#     refresh_token: str