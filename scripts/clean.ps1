# scripts/clean.ps1
param(
    [switch]$Hard
)

Write-Host "🧹 Limpiando proyecto..." -ForegroundColor Yellow

if ($Hard) {
    # Limpieza profunda (eliminar todo lo generado)
    Write-Host "⚠️  Modo Hard: Eliminando archivos generados..." -ForegroundColor Red
    
    # Backend
    if (Test-Path "backend\.venv") {
        Remove-Item -Recurse -Force backend\.venv
        Write-Host "   ✅ Eliminado backend\.venv" -ForegroundColor Gray
    }
    if (Test-Path "backend\__pycache__") {
        Remove-Item -Recurse -Force backend\__pycache__
        Write-Host "   ✅ Eliminado backend\__pycache__" -ForegroundColor Gray
    }
    
    # Frontend
    if (Test-Path "frontend\node_modules") {
        Remove-Item -Recurse -Force frontend\node_modules
        Write-Host "   ✅ Eliminado frontend\node_modules" -ForegroundColor Gray
    }
    if (Test-Path "frontend\.next") {
        Remove-Item -Recurse -Force frontend\.next
        Write-Host "   ✅ Eliminado frontend\.next" -ForegroundColor Gray
    }
    if (Test-Path "frontend\.pnpm-store") {
        Remove-Item -Recurse -Force frontend\.pnpm-store
        Write-Host "   ✅ Eliminado frontend\.pnpm-store" -ForegroundColor Gray
    }
}

# Detener y eliminar contenedores Docker
Write-Host "🐳 Deteniendo contenedores Docker..." -ForegroundColor Yellow
docker-compose down -v

Write-Host "✅ Proyecto limpio" -ForegroundColor Green