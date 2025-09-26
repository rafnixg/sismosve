# 🐳 Docker Setup para SismosVE

## Archivos Docker Incluidos

### 📄 Archivos Principales
- **`Dockerfile`** - Imagen multi-stage optimizada
- **`docker-compose.yml`** - Orquestación completa con Nginx opcional
- **`.dockerignore`** - Exclusión de archivos innecesarios
- **`nginx.conf`** - Configuración de proxy reverso
- **`docker.sh`** / **`docker.bat`** - Scripts de automatización

## 🚀 Uso Rápido

### Opción 1: Scripts Automatizados

#### Linux/Mac:
```bash
# Construir y ejecutar en desarrollo
./docker.sh run

# Ejecutar en producción con Nginx
./docker.sh prod

# Ver logs
./docker.sh logs

# Acceder al contenedor
./docker.sh shell
```

#### Windows:
```batch
REM Construir y ejecutar en desarrollo  
docker.bat run

REM Ejecutar en producción
docker.bat prod

REM Ver logs
docker.bat logs
```

### Opción 2: Comandos Docker Directos

#### Construcción Simple:
```bash
docker build -t sismosve:latest .
```

#### Ejecución en Desarrollo:
```bash
docker run -d \
  --name sismosve-dev \
  -p 8000:8000 \
  -v ./sismosve.json:/app/sismosve.json \
  -v ./logs:/app/logs \
  sismosve:latest
```

#### Producción con Docker Compose:
```bash
docker-compose up -d
```

## 📊 Configuración del Contenedor

### Características del Dockerfile:
- **Multi-stage build** para optimizar tamaño
- **Usuario no-root** para seguridad
- **Python 3.11 slim** como base
- **Health check** integrado
- **Variables de entorno** configurables

### Puertos y Volúmenes:
- **Puerto**: `8000` (FastAPI)
- **Datos**: `./sismosve.json` montado como volumen
- **Logs**: `./logs` para persistencia
- **Configuración**: Variables de entorno

### Variables de Entorno:
```bash
PYTHONUNBUFFERED=1
FASTAPI_ENV=production
PORT=8000
HOST=0.0.0.0
```

## 🔧 Docker Compose Features

### Servicios Incluidos:

#### 1. **sismosve** (Principal)
- Aplicación FastAPI
- Health checks automáticos
- Límites de recursos configurados
- Restart automático

#### 2. **nginx** (Opcional)
- Proxy reverso
- SSL/HTTPS support
- Caché de archivos estáticos
- Load balancing ready

### Perfiles de Despliegue:
```bash
# Solo aplicación
docker-compose up -d sismosve

# Con Nginx (producción)
docker-compose --profile production up -d
```

## 📁 Estructura de Archivos en Container

```
/app/
├── app/                    # Código FastAPI
├── static/                 # Archivos estáticos
├── templates/              # Templates HTML
├── sismosve.json          # Base de datos (montada)
├── logs/                  # Logs (montado)
├── run.py                 # Script de ejecución
└── requirements.txt       # Dependencias
```

## 🛡️ Seguridad y Optimización

### Características de Seguridad:
- ✅ **Usuario no-root** (`sismosve:sismosve`)
- ✅ **Imagen slim** con mínimas dependencias
- ✅ **Multi-stage build** reduce superficie de ataque
- ✅ **Health checks** para monitoreo
- ✅ **Resource limits** configurados

### Optimizaciones:
- ✅ **.dockerignore** reduce tamaño de contexto
- ✅ **Layer caching** optimizado
- ✅ **pip --user** instalación
- ✅ **No cache** para builds limpios disponible

## 🔍 Debugging y Monitoreo

### Ver Logs:
```bash
# Logs de aplicación
docker logs -f sismosve-dev

# Logs con docker-compose
docker-compose logs -f sismosve
```

### Acceder al Container:
```bash
# Shell interactivo
docker exec -it sismosve-dev /bin/bash

# Con docker-compose
docker-compose exec sismosve /bin/bash
```

### Health Check:
```bash
# Verificar estado
curl http://localhost:8000/api/health

# O usando el script
./docker.sh health
```

## 🚀 Despliegue en Producción

### 1. Con Docker Compose (Recomendado):
```bash
# Configurar ambiente
export FASTAPI_ENV=production

# Ejecutar servicios
docker-compose --profile production up -d

# Verificar estado
docker-compose ps
```

### 2. Con Kubernetes:
```yaml
# Ejemplo de deployment
apiVersion: apps/v1
kind: Deployment
metadata:
  name: sismosve
spec:
  replicas: 3
  selector:
    matchLabels:
      app: sismosve
  template:
    metadata:
      labels:
        app: sismosve
    spec:
      containers:
      - name: sismosve
        image: sismosve:latest
        ports:
        - containerPort: 8000
        env:
        - name: FASTAPI_ENV
          value: "production"
```

### 3. Con Docker Swarm:
```bash
# Inicializar swarm
docker swarm init

# Desplegar stack
docker stack deploy -c docker-compose.yml sismosve
```

## 📊 Monitoreo y Métricas

### Health Checks Automáticos:
- **Intervalo**: 30 segundos
- **Timeout**: 30 segundos
- **Reintentos**: 3
- **Endpoint**: `/api/health`

### Límites de Recursos:
- **Memoria**: 512M límite, 256M reserva
- **CPU**: 0.5 cores límite, 0.25 reserva

### Logs Estructurados:
- **Aplicación**: `/app/logs/sismos_api.log`
- **Container**: stdout/stderr capturados
- **Nginx**: access.log y error.log

## 🔧 Troubleshooting

### Problemas Comunes:

#### 1. Puerto en Uso:
```bash
# Verificar qué usa el puerto 8000
netstat -tlnp | grep :8000

# Cambiar puerto
docker run -p 8001:8000 sismosve:latest
```

#### 2. Permisos de Archivos:
```bash
# Verificar ownership
ls -la sismosve.json logs/

# Corregir permisos
chmod 666 sismosve.json
chmod -R 777 logs/
```

#### 3. Build Failures:
```bash
# Build con debug
docker build --progress=plain -t sismosve:latest .

# Build sin cache
docker build --no-cache -t sismosve:latest .
```

#### 4. Container No Inicia:
```bash
# Ver logs detallados
docker logs sismosve-dev

# Ejecutar interactivo para debug
docker run -it sismosve:latest /bin/bash
```

## 📈 Performance Tips

### Optimización de Build:
- Usar `.dockerignore` apropiado
- Aprovechar layer caching
- Multi-stage builds para reducir tamaño

### Optimización de Runtime:
- Configurar límites de memoria
- Usar health checks
- Montar volúmenes para datos persistentes

### Networking:
- Usar redes personalizadas
- Configurar DNS interno
- Load balancing con múltiples replicas

---

**🎯 Ready to Deploy!** Tu aplicación SismosVE está lista para contenedores con Docker completo y optimizado.