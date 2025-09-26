# SismosVE - Monitoreo de Sismos Venezuela

## 🎯 Descripción
Aplicación web moderna para visualizar y monitorear sismos en Venezuela usando datos oficiales de FUNVISIS.

## ✨ Características Principales
- **🗺️ Mapa interactivo** con marcadores de sismos (Leaflet.js)
- **🔍 Filtros avanzados** por magnitud y fechas
- **📊 Estadísticas** en tiempo real y análisis
- **🚀 API RESTful** optimizada con FastAPI
- **📱 Responsive design** para todos los dispositivos
- **🔄 Actualización automática** de datos FUNVISIS
- **⏰ Formato 12H** en timestamps
- **🎨 SEO optimizado** con Open Graph y Twitter Cards

## 🛠️ Tecnologías
- **Backend**: FastAPI + Python 3.9+
- **Frontend**: JavaScript ES6 modular + Leaflet.js
- **Datos**: JSON optimizado con caché inteligente
- **Estilos**: CSS3 con diseño responsive
- **Cache**: Cloudflare Tunnel compatible

## 📁 Estructura del Proyecto

```
sismosVE/
├── app/                    # Backend FastAPI
│   ├── main.py            # Aplicación principal
│   ├── services/          # Servicios de datos
│   └── models/            # Modelos de datos
├── static/                # Archivos estáticos
│   ├── js/               # JavaScript modular
│   │   ├── main.js       # Coordinador principal
│   │   ├── api-service.js # Gestión de API
│   │   ├── ui-manager.js  # Interfaz de usuario
│   │   ├── map-manager.js # Mapa Leaflet
│   │   └── utils.js       # Utilidades
│   ├── styles.css        # Estilos CSS
│   └── images/           # Recursos gráficos
├── templates/
│   └── index.html        # Template principal
├── sismosve.json         # Base de datos JSON
├── requirements.txt      # Dependencias Python
├── run.py               # Script de ejecución
├── updater.py           # Actualizador de datos
├── clear_cloudflare_cache.py # Script de limpieza
└── clean_project.sh     # Script de limpieza
```

## 🚀 Instalación y Uso

### 1. Instalar Dependencias
```bash
pip install -r requirements.txt
```

### 2. Ejecutar la Aplicación
```bash
# Desarrollo
python run.py dev

# Producción
python run.py prod
```

### 3. Acceder a la Aplicación
- **Web**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs

### 4. Limpiar Cache (Cloudflare)
```bash
python clear_cloudflare_cache.py
```

### 5. Limpiar Proyecto
```bash
bash clean_project.sh
```

## 📊 Endpoints de la API

### Datos Principales
- `GET /api/sismos` - Todos los sismos
- `GET /api/sismos/stats` - Estadísticas generales
- `GET /api/sismos/recent` - Sismos recientes
- `GET /api/sismos/magnitude/{min_mag}` - Filtrar por magnitud
- `GET /api/coordinates/{lat}/{lon}/{radius}` - Buscar por coordenadas

### Gestión
- `POST /api/update` - Actualizar datos manualmente
- `GET /api/health` - Estado del sistema

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

Las contribuciones son bienvenidas. Por favor:
1. Fork el proyecto
2. Crear una rama para tu feature
3. Commit tus cambios
4. Push a la rama
5. Abrir un Pull Request

## 📞 Soporte

Para soporte técnico o reportar bugs, crear un issue en el repositorio del proyecto.