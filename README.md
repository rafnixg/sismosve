# SismosVE - Monitoreo de Sismos Venezuela (sismosve.rafnixg.dev)

## 🎯 Descripción
Aplicación web moderna para visualizar y monitorear sismos en Venezuela usando datos oficiales de FUNVISIS.

## ✨ Características Principales
- **🗺️ Mapa interactivo** con marcadores de sismos (Leaflet.js)
- **🔍 Filtros avanzados** por magnitud y fechas
- **📊 Estadísticas** en tiempo real y análisis
- **🚀 API RESTful modular** optimizada con FastAPI
- **📱 Responsive design** para todos los dispositivos
- **🔄 Actualización automática** de datos FUNVISIS (cada 5 min)
- **⏰ Formato 12H** en timestamps
- **🎨 SEO optimizado** con Open Graph, Twitter Cards y Schema.org
- **🐳 Docker containerizado** con CI/CD automático
- **🏗️ Arquitectura modular** con separación de responsabilidades
- **🔒 Security headers** y health checks integrados
- **🌐 GitHub Container Registry** con builds multi-arquitectura

## 🛠️ Tecnologías
- **Backend**: FastAPI + Python 3.13+ con arquitectura modular
- **Frontend**: JavaScript ES6 modular + Leaflet.js
- **Containerización**: Docker + Docker Compose
- **CI/CD**: GitHub Actions con automated testing
- **Registry**: GitHub Container Registry (ghcr.io)
- **Datos**: JSON optimizado con caché inteligente
- **Estilos**: CSS3 con diseño responsive
- **Cache**: Cloudflare Tunnel compatible

## 🏗️ Arquitectura Modular

### Backend Organizado por Responsabilidades
- **`app/main.py`**: Configuración principal de FastAPI (50 líneas)
- **`app/config.py`**: Configuración centralizada y servicios
- **`app/routers/`**: Endpoints organizados por dominio
  - `sismos.py`: API de datos sísmicos
  - `admin.py`: Health checks y administración  
  - `seo.py`: Archivos especiales (robots.txt, sitemap.xml)
- **`app/exceptions.py`**: Manejadores de errores centralizados

### Beneficios de la Modularización
- ✅ **90% menos código** en archivo principal
- ✅ **Separación clara** de responsabilidades
- ✅ **Fácil testing** de módulos independientes
- ✅ **Escalabilidad** para nuevas funcionalidades
- ✅ **Mantenimiento** simplificado

## 📁 Estructura del Proyecto

```
sismosVE/
├── app/                    # Backend FastAPI modular
│   ├── main.py            # Aplicación principal (50 líneas)
│   ├── config.py          # Configuración y servicios
│   ├── exceptions.py      # Manejadores de excepciones
│   ├── routers/           # Endpoints organizados
│   │   ├── sismos.py      # API de datos sísmicos
│   │   ├── admin.py       # Administración y health checks
│   │   └── seo.py         # SEO y archivos especiales
│   ├── services/          # Servicios de datos
│   └── models/            # Modelos de datos
├── static/                # Archivos estáticos
│   ├── js/               # JavaScript ES6 modular
│   │   ├── main.js       # Coordinador principal
│   │   ├── api-service.js # Gestión de API
│   │   ├── ui-manager.js  # Interfaz de usuario (12H format)
│   │   ├── map-manager.js # Mapa interactivo Leaflet
│   │   └── utils.js       # Utilidades compartidas
│   ├── styles.css        # Estilos CSS responsive
│   ├── images/           # Recursos gráficos
│   ├── llms.txt          # Guidelines para IA
│   └── robots.txt        # SEO crawlers
├── templates/
│   └── index.html        # Template principal con SEO
├── .github/workflows/     # CI/CD con GitHub Actions
│   ├── ci.yml            # Tests y validación
│   ├── docker-build.yml  # Build y push Docker
│   └── release.yml       # Releases automatizados
├── Dockerfile            # Containerización
├── docker-compose.yml    # Orquestación
├── sismosve.json         # Base de datos JSON
├── requirements.txt      # Dependencias Python
├── run.py               # Script de ejecución
├── updater.py           # Actualizador de datos
├── clear_cloudflare_cache.py # Script de cache
└── clean_project.sh     # Limpieza de proyecto
```

## 🚀 Instalación y Uso

### Opción 1: Docker (Recomendado)
```bash
# Clonar repositorio
git clone https://github.com/rafnixg/sismosve.git
cd sismosve

# Ejecutar con Docker
docker-compose up -d

# Ver logs
docker-compose logs -f
```

### Opción 2: Instalación Local
```bash
# 1. Instalar dependencias
pip install -r requirements.txt

# 2. Ejecutar aplicación
# Desarrollo
python run.py dev

# Producción  
python run.py prod
```

### Opción 3: Imagen Pre-construida
```bash
# Desde GitHub Container Registry
docker run -d -p 8000:8000 ghcr.io/rafnixg/sismosve:latest
```

### 🌐 Acceder a la Aplicación
- **Web**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/api/health

### 🧹 Mantenimiento
```bash
python clear_cloudflare_cache.py
```

### 5. Limpiar Proyecto
```bash
bash clean_project.sh
```

## 📊 Endpoints de la API

### 🌍 Datos Sísmicos (`app/routers/sismos.py`)
- `GET /api/sismos` - Todos los sismos (GeoJSON)
- `GET /api/sismos/stats` - Estadísticas generales
- `GET /api/sismos/recent?limit=10` - Sismos recientes
- `GET /api/sismos/magnitude/{min_mag}` - Filtrar por magnitud
- `GET /api/sismos/coordinates` - Coordenadas para mapas

### ⚙️ Administración (`app/routers/admin.py`)
- `POST /api/update` - Actualizar datos manualmente
- `GET /api/status` - Estado del servicio updater
- `GET /api/health` - Health check completo

### 🔍 SEO y Archivos Especiales (`app/routers/seo.py`)
- `GET /robots.txt` - Para crawlers web
- `GET /sitemap.xml` - Sitemap dinámico
- `GET /humans.txt` - Información del equipo
- `GET /llms.txt` - Guidelines para IA
- `GET /.well-known/security.txt` - Seguridad

## 🎨 Características de la UI

### Mapa Interactivo
- **Marcadores por magnitud** con código de colores:
  - 🟢 Verde: < 4.0 (pequeños)
  - 🟠 Naranja: 4.0 - 4.9 (medianos)
  - 🔴 Rojo: ≥ 5.0 (grandes)
- **Popups informativos** con detalles completos
- **Sincronización mapa-lista**
- **Zoom automático** y controles

### Panel de Información
- **Lista ordenada** por fecha/hora
- **Filtros dinámicos** por magnitud
- **Estadísticas en tiempo real**
- **Formato 12H** en timestamps
- **Scroll personalizado**

### SEO y Marketing
- **Meta tags completos** para redes sociales
- **Open Graph** para Facebook/LinkedIn
- **Twitter Cards** para Twitter
- **Schema.org** structured data
- **robots.txt** y **sitemap.xml**

## 🔧 Mantenimiento

### Actualización de Datos
El sistema actualiza automáticamente los datos cada 30 minutos usando el `updater.py`.

### Cache Management
- **Cloudflare Tunnel**: Usar `clear_cloudflare_cache.py`
- **Browser Cache**: Headers optimizados automáticamente
- **Static Files**: Servidos sin versionado complejo

### Logs
- **Aplicación**: `sismos_api.log`
- **Cache**: `cache_clear.log`
- **Updater**: Integrado en `sismos_api.log`

### Limpieza
```bash
# Limpiar archivos temporales y logs
bash clean_project.sh

# Limpiar cache de Cloudflare
python clear_cloudflare_cache.py
```

## 🔄 CI/CD y Deployment

### GitHub Actions Workflows
- **`ci.yml`**: Tests automatizados en cada push/PR
- **`docker-build.yml`**: Build y push a GitHub Container Registry
- **`release.yml`**: Releases automatizados con tags
- **`maintenance.yml`**: Tareas de mantenimiento programadas

### Container Registry
```bash
# Tags disponibles
ghcr.io/rafnixg/sismosve:latest      # Última versión
ghcr.io/rafnixg/sismosve:v1.0.0      # Versión específica
ghcr.io/rafnixg/sismosve:main        # Branch main
```

### Multi-Architecture Support
- ✅ **linux/amd64** (x86_64)
- ✅ **linux/arm64** (ARM64/Apple Silicon)

### Automated Testing
- ✅ **Health checks** en múltiples entornos
- ✅ **API endpoint testing** con FastAPI TestClient
- ✅ **Container testing** con seguridad
- ✅ **SBOM generation** para dependencias

## 📱 Responsive Design

La aplicación está optimizada para:
- **Desktop** (1200px+)
- **Tablet** (768px - 1199px)
- **Mobile** (320px - 767px)

## 🛡️ Características de Seguridad

- **Headers de seguridad** configurados
- **CORS** habilitado apropiadamente
- **Validación de datos** con Pydantic
- **Rate limiting** implícito
- **Error handling** robusto

## 📄 Licencia

Este proyecto es de uso educativo y científico para el monitoreo de actividad sísmica en Venezuela.

## 🤝 Contribuciones

Las contribuciones son bienvenidas. La arquitectura modular facilita el desarrollo:

### Para Nuevas Funcionalidades
1. **Fork** el proyecto
2. **Crear rama** para tu feature: `git checkout -b feature/nueva-funcionalidad`
3. **Desarrollar** en el router apropiado:
   - Datos sísmicos → `app/routers/sismos.py`
   - Administración → `app/routers/admin.py`
   - SEO/Archivos → `app/routers/seo.py`
4. **Tests** → Usar FastAPI TestClient
5. **Commit** siguiendo [Conventional Commits](https://conventionalcommits.org/)
6. **Push** y crear **Pull Request**

### Estructura de Commits
```
feat: nueva funcionalidad
fix: corrección de bug  
docs: actualización documentación
style: cambios de formato
refactor: refactorización de código
test: agregar tests
chore: tareas de mantenimiento
```

## � Versioning

El proyecto sigue [Semantic Versioning](https://semver.org/):
- **MAJOR**: Cambios incompatibles en API
- **MINOR**: Nuevas funcionalidades compatibles  
- **PATCH**: Correcciones de bugs

### Changelog Reciente
- **v2.0.0**: 🏗️ Arquitectura modular, Docker, CI/CD
- **v1.0.0**: ✨ Aplicación base con mapa interactivo
- **v0.1.x**: 🚀 Versiones iniciales de desarrollo

## �📞 Soporte

### Reportar Issues
Para soporte técnico o reportar bugs:
1. **Buscar** issues existentes
2. **Crear issue** con template apropiado:
   - 🐛 Bug Report
   - ✨ Feature Request  
   - 📚 Documentation
   - ❓ Question

### Links Útiles
- **🌐 Demo**: https://sismosve.rafnixg.dev
- **📖 API Docs**: https://sismosve.rafnixg.dev/docs
- **🐳 Container**: https://github.com/rafnixg/sismosve/pkgs/container/sismosve
- **⚡ Actions**: https://github.com/rafnixg/sismosve/actions
