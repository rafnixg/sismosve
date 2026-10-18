FROM node:25-bookworm-slim AS frontend
WORKDIR /ui
COPY frontend/package*.json ./frontend/
RUN cd frontend && npm ci
COPY frontend/ ./frontend/
COPY tokens.css ./tokens.css
RUN cd frontend && npm run check && npm run test && npm run build

# Multi-stage Dockerfile para SismosVE
# Etapa 1: Builder - Instalar dependencias
FROM python:3.14-slim AS builder

# Instalar dependencias del sistema para compilación
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Crear directorio para las dependencias
WORKDIR /app

# Copiar requirements y instalar dependencias
COPY requirements.txt .
RUN python -m venv /opt/venv && /opt/venv/bin/pip install --no-cache-dir -r requirements.txt

# Etapa 2: Runtime - Imagen final optimizada
FROM python:3.14-slim

# Metadata
LABEL maintainer="SismosVE Team"
LABEL description="Aplicación web para monitoreo de sismos en Venezuela"
LABEL version="2.0"

# Crear usuario no-root para seguridad
RUN groupadd --gid 10001 sismosve && useradd --uid 10001 --gid 10001 --create-home --no-log-init sismosve

# Instalar dependencias mínimas del sistema
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# Crear directorios de la aplicación y establecer permisos
WORKDIR /app

# Copiar dependencias de Python desde builder
COPY --from=builder /opt/venv /opt/venv

# Copiar código de la aplicación
COPY --chown=sismosve:sismosve . .
COPY --from=frontend --chown=sismosve:sismosve /ui/static/ui /app/static/ui

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

# Crear directorio para logs y dar permisos de escritura al directorio completo
RUN mkdir -p /app/logs /app/data && \
    chown -R sismosve:sismosve /app && \
    chmod -R 755 /app && \
    chmod -R 777 /app/logs

# Cambiar al usuario no-root
USER sismosve

# Exponer puerto
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/api/health || exit 1

# Usar entrypoint personalizado
ENTRYPOINT ["/usr/local/bin/docker-entrypoint.sh"]
