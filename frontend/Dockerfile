# frontend/Dockerfile
ARG NODE_VERSION=25-alpine

FROM node:${NODE_VERSION}

WORKDIR /app

# Instalar pnpm globalmente
RUN npm install -g pnpm

# Copiar archivos de dependencias primero (mejor caché)
COPY package.json pnpm-lock.yaml* ./

# Instalar dependencias
RUN if [ -f pnpm-lock.yaml ]; then \
      pnpm install --frozen-lockfile; \
    else \
      pnpm install; \
    fi

# Copiar el resto del código
COPY . .

# ✅ CRÍTICO: Crear .next con permisos para evitar EACCES
RUN mkdir -p /app/.next && chmod 777 /app/.next

EXPOSE 3000

# Healthcheck
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
  CMD curl -f http://localhost:3000/ || exit 1

# ✅ CRÍTICO: Usar --hostname (no --host) para Next.js
CMD ["pnpm", "dev", "--hostname", "0.0.0.0", "--port", "3000"]