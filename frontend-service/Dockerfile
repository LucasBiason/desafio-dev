# frontend-service — multi-stage: build (Node), runtime (Nginx)
# Build from repo root: docker build -f frontend-service/Dockerfile .
# Compose: context: .  dockerfile: frontend-service/Dockerfile

# -----------------------------------------------------------------------------
# Stage: build — React build (Vite)
# -----------------------------------------------------------------------------
FROM node:20-alpine AS build

WORKDIR /app

COPY frontend-service/package*.json ./
RUN npm ci

COPY frontend-service/ .

ARG VITE_BASE_PATH=/
ENV VITE_BASE_PATH=$VITE_BASE_PATH

RUN npm run build

# -----------------------------------------------------------------------------
# Stage: runtime — Nginx serving static files
# -----------------------------------------------------------------------------
FROM nginx:alpine AS runtime

COPY frontend-service/nginx.conf /etc/nginx/conf.d/default.conf
COPY --from=build /app/dist /usr/share/nginx/html

LABEL org.opencontainers.image.title="frontend-service" \
      org.opencontainers.image.description="CNAB Parser web interface (React + Tailwind + Nord theme)" \
      org.opencontainers.image.vendor="CNAB Parser"

EXPOSE 3000

CMD ["nginx", "-g", "daemon off;"]
