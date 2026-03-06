# scripts/setup.ps1
param(
    [switch]$Force,
    [switch]$DevMode
)

Write-Host @"
╔══════════════════════════════════════════════════════════════╗
║                                                              ║
║   🚀 NEXT-PYTHON - Configuración del Proyecto               ║
║                                                              ║
╚══════════════════════════════════════════════════════════════╝
"@ -ForegroundColor Cyan

# Función para verificar si un comando existe
function Test-Command($command) {
    return (Get-Command $command -ErrorAction SilentlyContinue) -ne $null
}

# 1. Verificar Docker
Write-Host "`n🔍 Verificando requisitos..." -ForegroundColor Yellow
if (-not (Test-Command docker)) {
    Write-Host "❌ Docker no está instalado. Por favor instala Docker Desktop:" -ForegroundColor Red
    Write-Host "   https://www.docker.com/products/docker-desktop/" -ForegroundColor Cyan
    exit 1
}
Write-Host "✅ Docker instalado" -ForegroundColor Green

# 2. Verificar Docker Compose
if (-not (Test-Command docker-compose)) {
    Write-Host "⚠️ Docker Compose no encontrado, pero viene incluido en Docker Desktop" -ForegroundColor Yellow
}
Write-Host "✅ Docker Compose disponible" -ForegroundColor Green

# 3. Configurar archivo .env
Write-Host "`n📝 Configurando variables de entorno..." -ForegroundColor Yellow
if (-not (Test-Path ".env") -or $Force) {
    if (Test-Path ".env.example") {
        Copy-Item .env.example .env -Force
        Write-Host "✅ Archivo .env creado desde .env.example" -ForegroundColor Green
    } else {
        Write-Host "❌ No se encuentra .env.example" -ForegroundColor Red
        exit 1
    }
} else {
    Write-Host "✅ Archivo .env ya existe" -ForegroundColor Green
}

# 4. Modo desarrollo (solo para el creador)
if ($DevMode) {
    Write-Host "`n🛠️  Modo Desarrollo - Inicializando proyectos..." -ForegroundColor Magenta
    
    # Verificar Python
    if (-not (Test-Command python)) {
        Write-Host "❌ Python no está instalado. Necesitas Python para modo desarrollo:" -ForegroundColor Red
        Write-Host "   https://www.python.org/downloads/" -ForegroundColor Cyan
        exit 1
    }
    Write-Host "✅ Python encontrado" -ForegroundColor Green
    
    # Verificar Node.js
    if (-not (Test-Command node)) {
        Write-Host "❌ Node.js no está instalado. Necesitas Node.js para modo desarrollo:" -ForegroundColor Red
        Write-Host "   https://nodejs.org/" -ForegroundColor Cyan
        exit 1
    }
    Write-Host "✅ Node.js encontrado" -ForegroundColor Green
    
    # Verificar pnpm
    if (-not (Test-Command pnpm)) {
        Write-Host "📦 Instalando pnpm globalmente..." -ForegroundColor Yellow
        npm install -g pnpm
    }
    Write-Host "✅ pnpm instalado" -ForegroundColor Green
    
    # Ejecutar scripts de inicialización específicos
    & "$PSScriptRoot\init-backend.ps1"
    & "$PSScriptRoot\init-frontend.ps1"
} else {
    Write-Host "`n🐳 Modo Docker - Construyendo contenedores..." -ForegroundColor Blue
}

# 5. Construir y levantar con Docker
Write-Host "`n🏗️  Construyendo imágenes Docker..." -ForegroundColor Yellow
docker-compose build

Write-Host "`n🚀 Levantando contenedores..." -ForegroundColor Yellow
docker-compose up -d

# 6. Esperar a que los servicios estén listos
Write-Host "`n⏳ Esperando a que los servicios estén listos..." -ForegroundColor Yellow
Start-Sleep -Seconds 10

# 7. Verificar salud de los contenedores
$services = @("next-python_db", "next-python_backend", "next-python_frontend")
foreach ($service in $services) {
    $status = docker ps --filter "name=$service" --format "table {{.Status}}" | Select-Object -Skip 1
    if ($status -like "*healthy*" -or $status -like "*Up*") {
        Write-Host "✅ ${service}: $status" -ForegroundColor Green
    } else {
        Write-Host "⚠️ ${service}: $status" -ForegroundColor Yellow
    }
}

# 8. Mostrar información de acceso
Write-Host @"

╔══════════════════════════════════════════════════════════════╗
║                                                              ║
║   🎉 PROYECTO LISTO!                                         ║
║                                                              ║
║   📡 Frontend: http://localhost:3000                        ║
║   🔧 Backend:  http://localhost:8000                        ║
║   📚 API Docs: http://localhost:8000/docs                   ║
║   🗄️  Base de datos: localhost:5429                         ║
║                                                              ║
║   📝 Credenciales DB:                                        ║
║      User: admin                                             ║
║      Database: next_python_db                                ║
║      Port: 5429                                              ║
║                                                              ║
║   🐳 Comandos útiles:                                        ║
║      docker-compose logs -f frontend  # Ver logs frontend    ║
║      docker-compose logs -f backend   # Ver logs backend     ║
║      docker-compose ps                # Ver estado           ║
║      docker-compose down              # Detener todo         ║
║                                                              ║
╚══════════════════════════════════════════════════════════════╝
"@ -ForegroundColor Cyan