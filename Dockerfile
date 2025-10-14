# Multi-stage Dockerfile para SismosVE
# Etapa 1: Builder - Instalar dependencias
FROM python:3.14-slim as builder

# Instalar dependencias del sistema para compilación
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Crear directorio para las dependencias
WORKDIR /app

# Copiar requirements y instalar dependencias
COPY requirements.txt .
RUN pip install --no-cache-dir --user -r requirements.txt

# Etapa 2: Runtime - Imagen final optimizada
FROM python:3.14-slim

# Metadata
LABEL maintainer="SismosVE Team"
LABEL description="Aplicación web para monitoreo de sismos en Venezuela"
LABEL version="2.0"

# Crear usuario no-root para seguridad
RUN groupadd -r sismosve && useradd -r -g sismosve sismosve

# Instalar dependencias mínimas del sistema
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# Crear directorios de la aplicación y establecer permisos
WORKDIR /app

# Copiar dependencias de Python desde builder
COPY --from=builder /root/.local /home/sismosve/.local

# Copiar código de la aplicación
COPY --chown=sismosve:sismosve . .

# Copiar y hacer ejecutable el script de entrypoint
COPY docker-entrypoint.sh /usr/local/bin/
RUN chmod +x /usr/local/bin/docker-entrypoint.sh

# Variables de entorno
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV PATH=/home/sismosve/.local/bin:$PATH
ENV FASTAPI_ENV=production
ENV PORT=8000
ENV HOST=0.0.0.0
ENV LOG_FILE=/app/logs/sismos_api.log

# Crear directorio para logs y dar permisos de escritura al directorio completo
RUN mkdir -p /app/logs && \
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