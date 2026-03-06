# frontend/Dockerfile
ARG NODE_VERSION=25-alpine
FROM node:${NODE_VERSION}

# Crear directorio de trabajo
WORKDIR /app

# Instalar pnpm globalmente
RUN npm install -g pnpm

# Copiar archivos de dependencias primero
COPY package.json pnpm-lock.yaml* ./

# Instalar dependencias (como root)
RUN pnpm install --frozen-lockfile || pnpm install

# Copiar el resto del código
COPY . .

# Crear directorio .next con permisos adecuados y dar permisos
RUN mkdir -p /app/.next && \
    chmod 777 /app/.next && \
    chown -R node:node /app

# Cambiar al usuario node (no-root)
USER node

EXPOSE 3000

# Instalar curl para healthcheck (como root, luego volver a node)
USER root
RUN apk add --no-cache curl
USER node

HEALTHCHECK --interval=30s --timeout=10s --start-period=30s --retries=3 \
  CMD curl -f http://localhost:3000 || exit 1

CMD ["pnpm", "dev", "--hostname", "0.0.0.0", "--port", "3000"]