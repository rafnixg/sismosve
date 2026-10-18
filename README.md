# SismosVE - Monitoreo de Sismos Venezuela (sismosve.rafnixg.dev)

[![CI/CD Pipeline](https://github.com/rafnixg/sismosve/actions/workflows/ci.yml/badge.svg)](https://github.com/rafnixg/sismosve/actions/workflows/ci.yml)
[![Release](https://github.com/rafnixg/sismosve/actions/workflows/release.yml/badge.svg)](https://github.com/rafnixg/sismosve/actions/workflows/release.yml)
[![Python 3.14](https://img.shields.io/badge/python-3.14-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.143.2+-green.svg)](https://fastapi.tiangolo.com)
[![Docker](https://img.shields.io/badge/docker-%230db7ed.svg?logo=docker&logoColor=white)](https://github.com/rafnixg/sismosve/pkgs/container/sismosve)
[![GitHub stars](https://img.shields.io/github/stars/rafnixg/sismosve.svg?style=social&label=Star)](https://github.com/rafnixg/sismosve)

**Versión del código: `0.3.2`**. Consulta el [historial de cambios](CHANGELOG.md)
y las [releases publicadas](https://github.com/rafnixg/sismosve/releases).

## 🎯 Descripción
Aplicación web moderna para visualizar y monitorear sismos en Venezuela usando datos oficiales de FUNVISIS con arquitectura modular optimizada.

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
- **Backend**: FastAPI + Python 3.11+ con arquitectura modular (imagen Docker con Python 3.14 y Alpine 3.24)
- **Frontend**: Svelte 5 + TypeScript + Vite + Leaflet.js
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
- **`release.yml`**: Publicación exclusiva para tags `vX.Y.Z`, después de las pruebas
- **`docker-build.yml`**: Construcción multi-arquitectura reutilizable, llamada solo por releases
- **`container-scan.yml`**: Análisis por digest, SARIF y bloqueo ante vulnerabilidades altas/críticas
- **`maintenance.yml`**: Auditorías y salud de la imagen publicada, sin construir ni borrar imágenes

Los PR y los pushes a ramas no generan imágenes Docker. Consulta el [flujo de publicación y sus validaciones](GITHUB_ACTIONS_README.md) y el [informe de seguridad](security_best_practices_report.md).

### Container Registry

Después de que la versión del código complete el workflow de release:

```bash
# Última publicación estable aprobada
docker pull ghcr.io/rafnixg/sismosve:latest

# Versión específica y alias (VERSION contiene el número sin prefijo v)
SISMOSVE_VERSION=$(cat VERSION)
docker pull "ghcr.io/rafnixg/sismosve:v${SISMOSVE_VERSION}"
docker pull "ghcr.io/rafnixg/sismosve:${SISMOSVE_VERSION}"
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

El código y los materiales originales de SismosVE se publican bajo **GNU
Affero General Public License, versión 3 únicamente (AGPL-3.0-only)**, con una
condición adicional de atribución razonable conforme a su sección 7(b).
Copyright © 2025–2026 Rafnix Guzman (@rafnixg).

Puedes usarlos, modificarlos y redistribuirlos, incluso comercialmente,
cumpliendo [LICENSE](LICENSE) y [NOTICE](NOTICE). El software se proporciona
sin garantía. En los avisos legales apropiados de las interfaces que contengan
ese material debe conservarse este crédito legible:

> SismosVE - desarrollado originalmente por Rafnix Guzman (@rafnixg).

La condición no exige un logo ni una ubicación fija. Si ofreces una versión
modificada por red, debes ofrecer a sus usuarios el código fuente correspondiente
de esa versión, conforme a la sección 13. No basta con enlazar este repositorio
si tu versión contiene cambios que aquí no están disponibles.

La interfaz muestra el crédito y enlaza `/license`, `/notice` y `/source`,
disponibles también sin JavaScript. **`SOURCE_URL` debe apuntar a una descarga
del código exacto de la versión desplegada, accesible a sus usuarios**. En los
builds de release se fija al archivo del commit publicado. Para builds manuales
o forks, configura `--build-arg SOURCE_URL=https://…/archivo-del-commit.tar.gz`
o la variable de entorno `SOURCE_URL` al desplegar. En desarrollo, por defecto
enlaza el repositorio original. No incluyas credenciales en esa URL.

Los datos de FUNVISIS y los materiales de terceros conservan sus propios
derechos y condiciones: esta licencia no los relicencia. Las licencias del
frontend de terceros se generan durante el build y están disponibles en
`/static/ui/third-party-licenses.txt`.

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

## Versionado

El proyecto sigue [Semantic Versioning](https://semver.org/):
- **MAJOR**: Cambios incompatibles en API
- **MINOR**: Nuevas funcionalidades compatibles  
- **PATCH**: Correcciones de bugs

[`VERSION`](VERSION) es la fuente de la versión del código. FastAPI la usa en
OpenAPI (`/openapi.json`, visible en `/docs`) y en `/api/health`. El frontend,
las etiquetas Docker y la documentación se sincronizan con ese archivo.
Compose conserva la versión de la imagen y no declara otra versión de la aplicación.

Antes de preparar una release:

Sustituye `MAJOR.MINOR.PATCH` por el número de la nueva versión.

```bash
python .github/scripts/project_version.py --set MAJOR.MINOR.PATCH
# Actualizar CHANGELOG.md con los cambios de la versión
python .github/scripts/project_version.py --check
```

La comprobación se ejecuta también en CI. Después del merge, el tag debe ser
`v` seguido exactamente del contenido de `VERSION`; una diferencia bloquea
el release antes del build. No se modifican tags ya publicados. Consulta el
[procedimiento de publicación](GITHUB_ACTIONS_README.md#flujo-de-release).

### Historial reciente

- **v0.3.1**: Versionado consistente y remediación de la imagen para superar los controles de seguridad.
- **v0.3.0**: UI Svelte, SEO, persistencia del JSON, dependencias y publicación por tags.
- **v0.2.0**: Organización modular del backend FastAPI.
- **v0.1.x**: Versiones iniciales.

El detalle de cada versión está en [CHANGELOG.md](CHANGELOG.md).

El análisis de seguridad de `v0.3.0` bloqueó `latest` y la release de GitHub.
La versión `0.3.1` incorpora la corrección y vuelve a ejecutar esos controles;
el tag anterior se conserva. La existencia de un tag o imagen versionada no
implica aprobación: comprueba el resultado del workflow de release.

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


## UI Svelte: desarrollo y revisión local

Requisitos: Node 22.12+ (CI y builder Docker usan Node 22 LTS) y Python 3.11+.
El documento HTML, SEO y CTA de FUNVISIS se sirven desde FastAPI; Svelte
controla mapa, filtros y listado. El frontend conserva las rutas de la API.

```powershell
cd frontend
npm ci
npm run check
npm test
npm run build
cd ..
pip install -r requirements.txt pytest httpx
$env:TESTING = "true"
python -m pytest test_app.py test_ui.py test_storage.py -q
Remove-Item Env:TESTING
python -m uvicorn app.main:app --host 127.0.0.1 --port 8001
```

Para HMR, ejecutar `npm run dev` en `frontend` y arrancar FastAPI con
`VITE_DEV_URL=http://127.0.0.1:5173/static/ui`.
Para producción, no definir `VITE_DEV_URL`. `PUBLIC_URL` determina el canonical,
las tarjetas sociales y el sitemap; por defecto es https://sismosve.rafnixg.dev.
Las fechas y horas de los registros se muestran según la fuente.

### Contenedor de revisión aislado

En PowerShell, desde la raíz:

```powershell
docker compose -f docker-compose.local.yml up -d --build
```

Acceso: http://localhost:8001. Nombre: `sismosve-svelte-review`.
Los datos se guardan en el volumen de revisión `sismosve-review-data`, en
`/app/data/sismosve.json`. El JSON existente se conserva al iniciar. Si falta,
se inicializa una vez con la muestra del repositorio; la próxima consulta a
FUNVISIS ocurre a los cinco minutos o al pulsar el botón de actualización.
Si la fuente falla, se conservan los registros existentes.

```powershell
docker compose -f docker-compose.local.yml logs -f
docker compose -f docker-compose.local.yml stop
```

El Compose principal mantiene el puerto 8000 por defecto; se puede modificar
con `SISMOSVE_PORT`. La imagen compila el frontend durante el build y no requiere
Node en runtime. Los recursos compilados no se versionan; el lockfile sí.

### Persistencia del JSON y Dokploy

API y actualizadores comparten `DATA_FILE`. En Docker su valor es
`/app/data/sismosve.json`; los respaldos se guardan en el mismo volumen.
El usuario del contenedor usa UID/GID `10001:10001`. El volumen existente de
Dokploy debe montarse en `/app/data` y permitir escritura a ese usuario.
La [guía de migración](docs/PERSISTENT_DATA.md) incluye los comandos para copiar
el JSON anterior, preservar el archivo existente y verificar permisos.

### Comportamiento de la nueva interfaz

- Filtros combinados de magnitud mínima y fechas inclusivas, sin filtro inicial.
- Mapa, lista y estadísticas reflejan el mismo conjunto filtrado.
- Exportación JSON de los resultados visibles, conservando el contrato de datos.
- Consulta automática cada cinco minutos y actualización manual desde FUNVISIS.
- CTA permanente «¿Sentiste un sismo?» hacia la encuesta oficial en otra pestaña.
- SEO disponible sin JavaScript: metadatos, H1, descripción y enlaces principales.
