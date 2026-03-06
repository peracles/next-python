# scripts/dev.ps1
Write-Host "🚀 Modo Desarrollo Rápido" -ForegroundColor Cyan

# Reconstruir si hay cambios
docker-compose build

# Levantar en modo foreground (para ver logs)
docker-compose up

# Al salir con Ctrl+C, limpiar
Write-Host "`n🛑 Deteniendo contenedores..." -ForegroundColor Yellow
docker-compose down