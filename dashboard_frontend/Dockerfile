FROM node:22-bookworm-slim AS build

WORKDIR /app

COPY dashboard_frontend/package*.json ./
RUN npm ci \
  && npm install --no-save @rollup/rollup-linux-x64-gnu@4.52.4

COPY dashboard_frontend ./

ARG VITE_API_URL=/
ARG VITE_PYTHON_CAMERA_URL=/python-api
ARG VITE_PI_API_URL=/pi-api
ARG VITE_WS_URL=
ARG VITE_API_BASE_URL=
ENV VITE_API_URL=$VITE_API_URL
ENV VITE_PYTHON_CAMERA_URL=$VITE_PYTHON_CAMERA_URL
ENV VITE_PI_API_URL=$VITE_PI_API_URL
ENV VITE_WS_URL=$VITE_WS_URL
ENV VITE_API_BASE_URL=$VITE_API_BASE_URL

RUN npm run build

FROM nginx:1.27-alpine

COPY dashboard_frontend/nginx.conf.template /etc/nginx/templates/default.conf.template
COPY --from=build /app/dist /usr/share/nginx/html

EXPOSE 80
