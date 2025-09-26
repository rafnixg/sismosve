/**
 * Aplicación principal SismosVE
 * Coordina todos los módulos y maneja la lógica principal.
 */

import { ApiService, DataManager } from './api-service.js';
import { UIManager } from './ui-manager.js';
import { MapManager } from './map-manager.js';

export class SismosApp {
    constructor() {
        // Inicializar servicios
        this.apiService = new ApiService();
        this.dataManager = new DataManager(this.apiService);
        this.uiManager = new UIManager();
        this.mapManager = new MapManager();
        
        // Estado de la aplicación
        this.isLoading = false;
        
        this.init();
    }

    /**
     * Inicializa la aplicación
     */
    init() {
        this.bindEvents();
        this.loadData(); // Cargar datos automáticamente al inicializar
        
        // Configurar callback global para popups del mapa
        window.mapHighlightCallback = (index) => this.highlightEarthquake(index);
    }

    /**
     * Vincula eventos de la UI
     */
    bindEvents() {
        this.uiManager.bindEvents({
            onLoadData: () => this.loadData(),
            onExportData: () => this.exportData(),
            onForceUpdate: () => this.forceUpdate()
        });
    }

    /**
     * Carga datos de sismos
     */
    async loadData() {
        if (this.isLoading) return;
        
        this.isLoading = true;
        this.uiManager.showLoading('Obteniendo datos desde la API...');

        try {
            const data = await this.dataManager.loadData();
            this.updateUI(data);
            
            const count = this.dataManager.getEarthquakeCount();
            this.uiManager.showSuccess(`Datos cargados correctamente (${count} sismos)`);
            
        } catch (error) {
            console.error('Error al cargar los datos:', error);
            this.uiManager.showError('Error al cargar los datos. Verifica la conexión con la API.');
            
            // Intentar mostrar datos de respaldo si existen
            await this.handleFallbackData();
            
        } finally {
            this.isLoading = false;
        }
    }

    /**
     * Maneja datos de respaldo en caso de error
     */
    async handleFallbackData() {
        try {
            const data = await this.dataManager.loadFallbackData();
            this.updateUI(data);
            
            const count = this.dataManager.getEarthquakeCount();
            this.uiManager.showSuccess(`Mostrando datos de respaldo (${count} sismos)`);
            
        } catch (error) {
            console.error('Error al cargar datos de respaldo:', error);
            this.uiManager.showError('No se pudieron cargar los datos. API no disponible.');
        }
    }

    /**
     * Actualiza toda la interfaz de usuario
     * @param {Object} data - Datos de sismos
     */
    updateUI(data) {
        if (!data || !data.features) return;
        
        this.uiManager.updateStats(data);
        this.uiManager.renderEarthquakes(data);
        this.mapManager.updateMap(data, (index) => this.highlightEarthquake(index));
    }

    /**
     * Fuerza actualización de datos
     */
    async forceUpdate() {
        if (this.isLoading) return;
        
        this.isLoading = true;
        this.uiManager.showLoading('Forzando actualización...');
        
        try {
            const data = await this.dataManager.forceUpdate();
            this.updateUI(data);
            
            const count = this.dataManager.getEarthquakeCount();
            this.uiManager.showSuccess(`Datos actualizados correctamente (${count} sismos)`);
            
        } catch (error) {
            console.error('Error al forzar actualización:', error);
            this.uiManager.showError('Error al actualizar datos');
            
        } finally {
            this.isLoading = false;
        }
    }

    /**
     * Resalta un sismo específico en la lista
     * @param {number} index - Índice del sismo
     */
    highlightEarthquake(index) {
        this.uiManager.highlightEarthquake(index);
    }

    /**
     * Exporta datos actuales
     */
    exportData() {
        const data = this.dataManager.getCurrentData();
        if (!data) {
            this.uiManager.showError('No hay datos para exportar');
            return;
        }
        
        this.uiManager.exportData(data);
    }

    /**
     * Obtiene información del estado actual
     * @returns {Object} Estado de la aplicación
     */
    getAppState() {
        return {
            hasData: this.dataManager.hasData(),
            earthquakeCount: this.dataManager.getEarthquakeCount(),
            isLoading: this.isLoading,
            lastUpdate: this.dataManager.lastUpdate,
            mapReady: this.mapManager.isReady()
        };
    }

    /**
     * Reinicia la aplicación
     */
    reset() {
        this.mapManager.clearMarkers();
        this.mapManager.resetView();
        this.dataManager.currentData = null;
        this.uiManager.showSuccess('Aplicación reiniciada');
    }

    /**
     * Destruye la aplicación y libera recursos
     */
    destroy() {
        this.mapManager.destroy();
        window.mapHighlightCallback = null;
    }
}

// Variable global para acceso desde popups y debugging
let app;

// Inicializar la aplicación cuando el DOM esté listo
document.addEventListener('DOMContentLoaded', () => {
    try {
        app = new SismosApp();
        window.sismosApp = app; // Disponible globalmente para debugging
        console.log('Aplicación SismosVE inicializada correctamente');
    } catch (error) {
        console.error('Error al inicializar la aplicación:', error);
    }
});

// Exportar para uso como módulo
export default app;