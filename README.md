# 🚀 FullStack Monorepo: Next.js + FastAPI

Proyecto base escalable utilizando arquitectura de microservicios modulares, Screaming Architecture y contenerización completa.

## 🛠 Stack Tecnológico

- **Frontend:** Next.js 14 (App Router), TypeScript, TailwindCSS, Shadcn/ui
- **Backend:** FastAPI, Python 3.11, SQLAlchemy (Async), Pydantic
- **Database:** PostgreSQL 15
- **Infraestructura:** Docker, Docker Compose
- **Auth:** JWT (JSON Web Tokens)

## 🏗 Arquitectura

El proyecto sigue un enfoque de **Monorepo Modular**.
- **Backend:** Organizado por dominios de negocio (`modules/auth`, `modules/users`) listo para ser extraído a microservicios independientes.
- **Frontend:** Separación de UI (`components`) y Lógica de Negocio (`features`).

## 📋 Prerrequisitos

- Docker & Docker Compose
- Node.js v20+ (para dev local)
- Python v3.11+ (para dev local)

## ⚡ Inicio Rápido (Docker)

1. Clonar el repositorio.
2. Copiar el archivo de entorno maestro:
   ```bash
   cp .env.example .env

cat > README.md << EOF
# 🚀 FullStack Monorepo: Next.js + FastAPI

Proyecto base escalable con arquitectura modular. Todo el entorno corre dentro de contenedores Docker.

## 🛠 Stack
- **Frontend:** Next.js 14, TypeScript, TailwindCSS, Shadcn/ui
- **Backend:** FastAPI, Python 3.11, SQLAlchemy Async, PostgreSQL
- **Infra:** Docker Compose

## ⚡ Inicio Rápido

1. **Configurar Variables**
   \`\`\`bash
   cp .env.example .env
   \`\`\`

2. **Levantar Servicios**
   \`\`\`bash
   make up
   # o
   docker compose up --build
   \`\`\`

3. **Acceder**
   - Frontend: http://localhost:3000
   - Backend Docs: http://localhost:8000/docs
   - Database: localhost:5432

## 📂 Estructura
- \`/backend\`: API REST con Screaming Architecture
- \`/frontend\`: Next.js App Router
EOF