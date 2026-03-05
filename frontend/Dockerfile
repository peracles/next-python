ARG NODE_VERSION=24.13.0-alpine

FROM node:${NODE_VERSION}

RUN npm install -g pnpm@latest

WORKDIR /app

# ✅ Manejar caso donde pnpm-lock.yaml aún no existe
COPY package.json ./
RUN pnpm install --frozen-lockfile 2>$null || pnpm install

COPY . .

EXPOSE 3000

HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD wget --no-verbose --tries=1 --spider http://localhost:3000/api/health || exit 1

CMD ["pnpm", "dev", "--host", "--port", "3000"]