# Copyright (C) 2025-2026 Rafnix Guzman (@rafnixg).
# SPDX-License-Identifier: AGPL-3.0-only
# Additional author-attribution term under section 7(b): see repository-root NOTICE.
FROM --platform=$BUILDPLATFORM node:22-bookworm-slim AS frontend
WORKDIR /ui
COPY frontend/package*.json ./frontend/
RUN cd frontend && npm ci
COPY frontend/ ./frontend/
COPY tokens.css ./tokens.css
RUN cd frontend && npm run check && npm run test && npm run build

# Multi-stage Dockerfile para SismosVE
# Etapa 1: Builder - Instalar dependencias
FROM python:3.14-alpine3.24 AS builder

# Crear directorio para las dependencias
WORKDIR /app

# Copiar requirements y instalar dependencias
COPY requirements.txt .
RUN python -m venv /opt/venv && \
    /opt/venv/bin/pip install --only-binary=:all: --no-cache-dir -r requirements.txt && \
    /opt/venv/bin/python -m pip uninstall -y pip

# Etapa 2: Runtime - Imagen final optimizada
FROM python:3.14-alpine3.24

# Metadata
ARG APP_VERSION=0.3.2
ARG SOURCE_URL=https://github.com/rafnixg/sismosve
LABEL maintainer="SismosVE Team"
LABEL description="Aplicación web para monitoreo de sismos en Venezuela"
LABEL version="${APP_VERSION}"
LABEL org.opencontainers.image.version="${APP_VERSION}"
LABEL org.opencontainers.image.licenses="AGPL-3.0-only"

# Crear usuario no-root para seguridad
RUN addgroup -g 10001 sismosve && \
    adduser -D -u 10001 -G sismosve sismosve

# Runtime needs neither package installers nor their vendored dependencies.
# Health checks use Python, so curl and its libraries are unnecessary.
RUN apk upgrade --no-cache && \
    apk add --no-cache libstdc++ && \
    python -m pip uninstall -y pip && \
    python -c "import pathlib, shutil, sysconfig; shutil.rmtree(pathlib.Path(sysconfig.get_path('stdlib')) / 'ensurepip')"

# Crear directorios de la aplicación y establecer permisos
WORKDIR /app

# Copiar dependencias de Python desde builder
COPY --from=builder /opt/venv /opt/venv

# Copiar código de la aplicación
COPY --chown=sismosve:sismosve . .
COPY --from=frontend --chown=sismosve:sismosve /ui/static/ui /app/static/ui
RUN test "$APP_VERSION" = "$(cat VERSION)"

# Copiar y hacer ejecutable el script de entrypoint
COPY docker-entrypoint.sh /usr/local/bin/
RUN sed -i 's/\r$//' /usr/local/bin/docker-entrypoint.sh && chmod +x /usr/local/bin/docker-entrypoint.sh

# Variables de entorno
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV PATH=/opt/venv/bin:$PATH
ENV FASTAPI_ENV=production
ENV PORT=8000
ENV HOST=0.0.0.0
ENV LOG_FILE=/app/logs/sismos_api.log
ENV DATA_FILE=/app/data/sismosve.json
ENV SOURCE_URL=${SOURCE_URL}

# Crear directorio para logs y dar permisos de escritura al directorio completo
RUN mkdir -p /app/logs /app/data && \
    chown -R sismosve:sismosve /app && \
    chmod -R 755 /app

# Cambiar al usuario no-root
USER sismosve

# Exponer puerto
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD ["python", "-m", "app.healthcheck"]

# Usar entrypoint personalizado
ENTRYPOINT ["/usr/local/bin/docker-entrypoint.sh"]
