# scripts/init-frontend.ps1
Write-Host "`n📦 Inicializando Frontend (Next.js + pnpm)..." -ForegroundColor Magenta

# Ir al directorio frontend
Set-Location frontend

# Verificar si es un proyecto Next.js válido
if (-not (Test-Path "package.json")) {
    Write-Host "📝 Creando proyecto Next.js..." -ForegroundColor Yellow
    
    # Crear proyecto Next.js con todas las configuraciones
    pnpm create next-app@latest . --typescript --tailwind --eslint --app --no-src-dir --import-alias "@/*"
    
    # Instalar dependencias adicionales comunes
    Write-Host "📦 Instalando dependencias adicionales..." -ForegroundColor Yellow
    pnpm add axios @tanstack/react-query
    pnpm add -D @types/node
} else {
    Write-Host "📦 Instalando dependencias del frontend..." -ForegroundColor Yellow
    pnpm install
}

# Crear .env.local si no existe
if (-not (Test-Path ".env.local") -and (Test-Path ".env.local.example")) {
    Copy-Item .env.local.example .env.local -Force
    Write-Host "✅ .env.local creado" -ForegroundColor Green
}

# Verificar configuración de Tailwind
if (-not (Test-Path "tailwind.config.ts")) {
    Write-Host "🎨 Configurando Tailwind CSS..." -ForegroundColor Yellow
    pnpm dlx tailwindcss init -p
}

# Volver al directorio raíz
Set-Location ..

Write-Host "✅ Frontend inicializado correctamente" -ForegroundColor Green