/**
 * Manager para la interfaz de usuario
 */

import { DateTimeUtils, MagnitudeUtils, FileUtils } from './utils.js';

export class UIManager {
    constructor() {
        this.elements = {
            status: document.getElementById('status'),
            loadBtn: document.getElementById('loadData'),
            exportBtn: document.getElementById('exportData'),
            forceUpdateBtn: null, // Se crea dinámicamente
            stats: document.getElementById('stats'),
            totalCount: document.getElementById('totalCount'),
            lastEarthquake: document.getElementById('lastEarthquake'),
            maxMagnitude: document.getElementById('maxMagnitude'),
            earthquakeList: document.getElementById('earthquakeList')
        };
        
        this.createForceUpdateButton();
    }

    /**
     * Crea el botón de actualización forzada
     */
    createForceUpdateButton() {
        const forceUpdateBtn = document.createElement('button');
        forceUpdateBtn.id = 'forceUpdate';
        forceUpdateBtn.className = 'btn-secondary';
        forceUpdateBtn.textContent = 'Actualizar Datos';
        
        const controlsDiv = document.querySelector('.controls');
        controlsDiv.insertBefore(forceUpdateBtn, this.elements.exportBtn);
        
        this.elements.forceUpdateBtn = forceUpdateBtn;
    }

    /**
     * Muestra estado de carga
     * @param {string} message - Mensaje a mostrar
     */
    showLoading(message = 'Cargando...') {
        this.elements.status.innerHTML = `<span class="loading-spinner"></span>${message}`;
        this.elements.status.className = 'status loading';
        this.elements.loadBtn.disabled = true;
        if (this.elements.forceUpdateBtn) {
            this.elements.forceUpdateBtn.disabled = true;
        }
    }

    /**
     * Muestra estado de éxito
     * @param {string} message - Mensaje a mostrar
     */
    showSuccess(message) {
        this.elements.status.textContent = message;
        this.elements.status.className = 'status success';
        this.elements.exportBtn.disabled = false;
        this.enableButtons();
    }

    /**
     * Muestra estado de error
     * @param {string} message - Mensaje de error
     */
    showError(message) {
        this.elements.status.textContent = message;
        this.elements.status.className = 'status error';
        this.enableButtons();
    }

    /**
     * Habilita todos los botones
     */
    enableButtons() {
        this.elements.loadBtn.disabled = false;
        if (this.elements.forceUpdateBtn) {
            this.elements.forceUpdateBtn.disabled = false;
        }
    }

    /**
     * Actualiza las estadísticas
     * @param {Object} data - Datos de sismos
     */
    updateStats(data) {
        const features = data.features;
        
        // Total de sismos
        this.elements.totalCount.textContent = features.length;
        
        // Último sismo
        const latest = DateTimeUtils.getLatestEarthquake(features);
        this.elements.lastEarthquake.textContent = latest ? 
            `${DateTimeUtils.convertTo12Hour(latest.properties.time)} / ${latest.properties.date}` : '-';
        
        // Mayor magnitud
        const maxMag = Math.max(...features.map(f => parseFloat(f.properties.value) || 0));
        this.elements.maxMagnitude.textContent = maxMag.toFixed(1);
        
        this.elements.stats.style.display = 'grid';
    }

    /**
     * Renderiza la lista de sismos
     * @param {Object} data - Datos de sismos
     */
    renderEarthquakes(data) {
        const features = data.features;
        
        if (features.length === 0) {
            this.elements.earthquakeList.innerHTML = `
                <div class="empty-state">
                    <h3>No hay datos disponibles</h3>
                    <p>No se encontraron registros de sismos</p>
                </div>
            `;
            return;
        }

        // Ordenar por fecha/hora más reciente
        const sortedFeatures = [...features].sort((a, b) => {
            const dateA = DateTimeUtils.parseDateTime(a.properties.date, a.properties.time);
            const dateB = DateTimeUtils.parseDateTime(b.properties.date, b.properties.time);
            return dateB - dateA;
        });

        this.elements.earthquakeList.innerHTML = sortedFeatures.map(feature => {
            const magnitude = parseFloat(feature.properties.value) || 0;
            const magnitudeClass = MagnitudeUtils.getMagnitudeClass(magnitude);
            
            return `
                <div class="earthquake-item ${magnitudeClass}-magnitude">
                    <div class="earthquake-header">
                        <div class="magnitude ${magnitudeClass}">
                            ${magnitude.toFixed(1)}
                        </div>
                        <div class="earthquake-info">
                            <div class="location">${feature.properties.addressFormatted}</div>
                            <div class="datetime">
                                📅 ${feature.properties.date} ⏰ ${DateTimeUtils.convertTo12Hour(feature.properties.time)}
                            </div>
                        </div>
                    </div>
                    <div class="earthquake-details">
                        <div class="detail-item">
                            <div class="detail-label">Profundidad</div>
                            <div class="detail-value">${feature.properties.depth}</div>
                        </div>
                        <div class="detail-item">
                            <div class="detail-label">Latitud</div>
                            <div class="detail-value">${feature.properties.lat}°</div>
                        </div>
                        <div class="detail-item">
                            <div class="detail-label">Longitud</div>
                            <div class="detail-value">${feature.properties.long}°</div>
                        </div>
                        <div class="detail-item">
                            <div class="detail-label">País</div>
                            <div class="detail-value">${feature.properties.country}</div>
                        </div>
                    </div>
                </div>
            `;
        }).join('');
    }

    /**
     * Resalta un sismo específico en la lista
     * @param {number} index - Índice del sismo a resaltar
     */
    highlightEarthquake(index) {
        const earthquakeItems = document.querySelectorAll('.earthquake-item');
        if (earthquakeItems[index]) {
            // Scroll hasta el elemento
            earthquakeItems[index].scrollIntoView({ 
                behavior: 'smooth', 
                block: 'center' 
            });
            
            // Agregar efecto de highlight
            earthquakeItems[index].classList.add('highlighted');
            setTimeout(() => {
                earthquakeItems[index].classList.remove('highlighted');
            }, 3000);
        }
    }

    /**
     * Exporta datos como archivo JSON
     * @param {Object} data - Datos a exportar
     */
    exportData(data) {
        const filename = FileUtils.generateFilename('sismos_transformados');
        FileUtils.downloadJSON(data, filename);
    }

    /**
     * Vincula eventos a los botones
     * @param {Object} callbacks - Objeto con callbacks para cada evento
     */
    bindEvents(callbacks) {
        if (this.elements.loadBtn && callbacks.onLoadData) {
            this.elements.loadBtn.addEventListener('click', callbacks.onLoadData);
        }

        if (this.elements.exportBtn && callbacks.onExportData) {
            this.elements.exportBtn.addEventListener('click', callbacks.onExportData);
        }

        if (this.elements.forceUpdateBtn && callbacks.onForceUpdate) {
            this.elements.forceUpdateBtn.addEventListener('click', callbacks.onForceUpdate);
        }
    }
}