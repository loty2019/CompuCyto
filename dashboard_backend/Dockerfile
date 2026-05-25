FROM node:22-bookworm-slim AS build

WORKDIR /app

COPY package*.json ./
COPY dashboard_backend/package*.json ./dashboard_backend/
RUN npm ci --workspace dashboard_backend

COPY dashboard_backend ./dashboard_backend
RUN npm run --workspace dashboard_backend build

FROM node:22-bookworm-slim

WORKDIR /app
ENV NODE_ENV=production

COPY package*.json ./
COPY dashboard_backend/package*.json ./dashboard_backend/
RUN npm ci --omit=dev --workspace dashboard_backend && npm cache clean --force

COPY --from=build /app/dashboard_backend/dist ./dashboard_backend/dist

WORKDIR /app/dashboard_backend
EXPOSE 3000

CMD ["node", "dist/main"]
