# backend/app/main.py
"""
Punto de entrada de la aplicación FastAPI

Este archivo orquesta la aplicación:
- Inicializa la app con metadatos
- Incluye routers de módulos
- Expone endpoints de health check
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.modules.users.router import router as users_router
from app.modules.auth.router import router as auth_router


# ─────────────────────────────────────────────────────────────
# 1. Crear instancia de FastAPI
# ─────────────────────────────────────────────────────────────
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="API Fullstack con Next.js + FastAPI + PostgreSQL",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json"
)

# ─────────────────────────────────────────────────────────────
# 2. Configurar CORS
# ─────────────────────────────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # ← En producción: ["https://tudominio.com"]
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ─────────────────────────────────────────────────────────────
# 3. Incluir routers de módulos (Screaming Architecture)
# ─────────────────────────────────────────────────────────────
# ✅ AHORA SÍ: Descomentar estos imports ahora que los archivos existen
app.include_router(auth_router)  # ← Rutas: /auth/login, /auth/me, etc.
app.include_router(users_router)  # ← Rutas: /users, /users/{id}, etc.

# ─────────────────────────────────────────────────────────────
# 4. Endpoints de health check
# ─────────────────────────────────────────────────────────────
@app.get("/")
async def root():
    return {
        "message": "Welcome to Next-Python API",
        "docs": "/docs",
        "version": settings.APP_VERSION,
        "environment": settings.ENVIRONMENT
    }


@app.get("/health")
async def health_check():
    return {"status": "healthy"}


@app.get("/health/db")
async def health_check_db():
    # Placeholder: se implementará cuando tengamos conexión real a DB
    return {"status": "healthy", "db": "pending"}