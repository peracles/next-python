# scripts/init-backend.ps1
Write-Host "`n📦 Inicializando Backend (FastAPI)..." -ForegroundColor Magenta

# Ir al directorio backend
Set-Location backend

# Crear y activar entorno virtual si no existe
if (-not (Test-Path ".venv")) {
    Write-Host "🔧 Creando entorno virtual..." -ForegroundColor Yellow
    python -m venv .venv
}

# Activar entorno virtual (para Windows)
Write-Host "🔧 Activando entorno virtual..." -ForegroundColor Yellow
& .\.venv\Scripts\Activate.ps1

# Instalar dependencias básicas si no existe requirements.txt
if (-not (Test-Path "requirements.txt")) {
    Write-Host "📝 Creando requirements.txt..." -ForegroundColor Yellow
    @"
fastapi==0.109.0
uvicorn==0.27.0
python-dotenv==1.0.0
"@ | Out-File -FilePath requirements.txt -Encoding UTF8
}

# Instalar dependencias
Write-Host "📦 Instalando dependencias del backend..." -ForegroundColor Yellow
pip install -r requirements.txt
pip freeze > requirements.txt

# Crear estructura de app si no existe
if (-not (Test-Path "app")) {
    Write-Host "📁 Creando estructura de la aplicación..." -ForegroundColor Yellow
    New-Item -ItemType Directory -Path app -Force
    
    # Crear __init__.py
    New-Item -ItemType File -Path app\__init__.py -Force
    
    # Crear main.py
    @"
from fastapi import FastAPI

app = FastAPI(
    title="Next-Python API",
    description="API para el proyecto Next.js + FastAPI",
    version="1.0.0"
)

@app.get("/")
def root():
    return {"message": "Bienvenido a la API de Next-Python"}

@app.get("/health")
def health():
    return {"status": "healthy", "environment": "development"}
"@ | Out-File -FilePath app\main.py -Encoding UTF8
}

# Volver al directorio raíz
Set-Location ..

Write-Host "✅ Backend inicializado correctamente" -ForegroundColor Green