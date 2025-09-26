/**
 * Manager para el mapa interactivo usando Leaflet
 */

import { DateTimeUtils, MagnitudeUtils, ValidationUtils } from './utils.js';

export class MapManager {
    constructor() {
        this.map = null;
        this.markersGroup = null;
        this.initialized = false;
        this.init();
    }

    /**
     * Inicializa el mapa
     */
    init() {
        try {
            // Inicializar el mapa centrado en Venezuela
            this.map = L.map('map').setView([8.0, -66.0], 6);
            
            // Agregar capa de tiles
            L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
                attribution: '© OpenStreetMap contributors',
                maxZoom: 18,
            }).addTo(this.map);
            
            // Crear grupo de marcadores
            this.markersGroup = L.layerGroup().addTo(this.map);
            
            // Agregar control de escala
            L.control.scale().addTo(this.map);
            
            this.initialized = true;
            console.log('Mapa inicializado correctamente');
        } catch (error) {
            console.error('Error al inicializar el mapa:', error);
        }
    }

    /**
     * Verifica si el mapa está inicializado
     * @returns {boolean} True si está inicializado
     */
    isReady() {
        return this.initialized && this.map && this.markersGroup;
    }

    /**
     * Actualiza el mapa con nuevos datos de sismos
     * @param {Object} data - Datos de sismos
     * @param {Function} highlightCallback - Callback para resaltar sismos
     */
    updateMap(data, highlightCallback = null) {
        if (!this.isReady() || !ValidationUtils.isValidEarthquakeData(data)) {
            console.warn('Mapa no listo o datos inválidos');
            return;
        }
        
        // Limpiar marcadores existentes
        this.markersGroup.clearLayers();
        
        const features = data.features;
        const bounds = [];
        
        features.forEach((feature, index) => {
            const lat = parseFloat(feature.properties.lat);
            const lng = parseFloat(feature.properties.long);
            
            if (!ValidationUtils.isValidCoordinates(lat, lng)) {
                console.warn(`Coordenadas inválidas para sismo ${index}:`, lat, lng);
                return;
            }
            
            bounds.push([lat, lng]);
            
            const marker = this.createMarker(feature, index, highlightCallback);
            this.markersGroup.addLayer(marker);
        });
        
        // Ajustar vista para mostrar todos los puntos
        if (bounds.length > 0) {
            this.map.fitBounds(bounds, { padding: [20, 20] });
        }
    }

    /**
     * Crea un marcador para un sismo
     * @param {Object} feature - Datos del sismo
     * @param {number} index - Índice del sismo
     * @param {Function} highlightCallback - Callback para resaltar
     * @returns {L.CircleMarker} Marcador creado
     */
    createMarker(feature, index, highlightCallback) {
        const lat = parseFloat(feature.properties.lat);
        const lng = parseFloat(feature.properties.long);
        const magnitude = parseFloat(feature.properties.value) || 0;
        
        // Determinar el color y tamaño basado en la magnitud
        const { color, radius } = MagnitudeUtils.getMarkerStyle(magnitude);
        
        // Crear marcador circular
        const marker = L.circleMarker([lat, lng], {
            radius: radius,
            fillColor: color,
            color: '#fff',
            weight: 2,
            opacity: 1,
            fillOpacity: 0.8
        });
        
        // Crear popup con información del sismo
        const popupContent = this.createPopupContent(feature, index, highlightCallback);
        marker.bindPopup(popupContent);
        
        // Agregar evento hover
        marker.on('mouseover', function() {
            this.openPopup();
        });
        
        return marker;
    }

    /**
     * Crea el contenido del popup para un sismo
     * @param {Object} feature - Datos del sismo
     * @param {number} index - Índice del sismo
     * @param {Function} highlightCallback - Callback para resaltar
     * @returns {string} HTML del popup
     */
    createPopupContent(feature, index, highlightCallback) {
        const magnitude = parseFloat(feature.properties.value) || 0;
        const magnitudeClass = MagnitudeUtils.getMagnitudeClass(magnitude);
        
        return `
            <div class="popup-content">
                <div class="popup-header">
                    <span class="popup-magnitude ${magnitudeClass}">${magnitude.toFixed(1)}</span>
                    <span class="popup-location">${feature.properties.addressFormatted}</span>
                </div>
                <div class="popup-details">
                    <div><strong>📅 Fecha:</strong> ${feature.properties.date}</div>
                    <div><strong>⏰ Hora:</strong> ${DateTimeUtils.convertTo12Hour(feature.properties.time)}</div>
                    <div><strong>📏 Profundidad:</strong> ${feature.properties.depth}</div>
                    <div><strong>🌍 Coordenadas:</strong> ${feature.properties.lat}°, ${feature.properties.long}°</div>
                </div>
                ${highlightCallback ? `
                    <button onclick="window.mapHighlightCallback(${index})" class="popup-button">
                        Ver en lista
                    </button>
                ` : ''}
            </div>
        `;
    }

    /**
     * Centra el mapa en un sismo específico
     * @param {Object} feature - Datos del sismo
     * @param {number} zoomLevel - Nivel de zoom (opcional)
     */
    centerOnEarthquake(feature, zoomLevel = 10) {
        if (!this.isReady()) return;
        
        const lat = parseFloat(feature.properties.lat);
        const lng = parseFloat(feature.properties.long);
        
        if (ValidationUtils.isValidCoordinates(lat, lng)) {
            this.map.setView([lat, lng], zoomLevel);
        }
    }

    /**
     * Resetea la vista del mapa a Venezuela
     */
    resetView() {
        if (!this.isReady()) return;
        this.map.setView([8.0, -66.0], 6);
    }

    /**
     * Limpia todos los marcadores del mapa
     */
    clearMarkers() {
        if (this.markersGroup) {
            this.markersGroup.clearLayers();
        }
    }

    /**
     * Obtiene las dimensiones del mapa
     * @returns {Object} Objeto con width y height
     */
    getMapSize() {
        if (!this.isReady()) return { width: 0, height: 0 };
        
        const container = this.map.getContainer();
        return {
            width: container.offsetWidth,
            height: container.offsetHeight
        };
    }

    /**
     * Invalida el tamaño del mapa (útil después de cambios de layout)
     */
    invalidateSize() {
        if (this.isReady()) {
            setTimeout(() => {
                this.map.invalidateSize();
            }, 100);
        }
    }

    /**
     * Destruye el mapa y libera recursos
     */
    destroy() {
        if (this.map) {
            this.map.remove();
            this.map = null;
            this.markersGroup = null;
            this.initialized = false;
        }
    }
}