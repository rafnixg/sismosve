/**
 * Servicio para manejo de API y datos de sismos
 */

import { ValidationUtils } from './utils.js';

export class ApiService {
    constructor() {
        this.baseUrl = '';
        this.endpoints = {
            sismos: '/api/sismos',
            update: '/api/update',
            stats: '/api/sismos/stats',
            health: '/api/health'
        };
    }

    /**
     * Obtiene datos de sismos desde la API
     * @returns {Promise<Object>} Datos de sismos
     */
    async getSismos() {
        try {
            const response = await fetch(this.endpoints.sismos);
            
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            const data = await response.json();
            
            if (!ValidationUtils.isValidEarthquakeData(data)) {
                throw new Error('Datos de sismos inválidos');
            }

            return data;
        } catch (error) {
            console.error('Error al obtener sismos:', error);
            throw error;
        }
    }

    /**
     * Obtiene estadísticas de sismos
     * @returns {Promise<Object>} Estadísticas de sismos
     */
    async getStats() {
        try {
            const response = await fetch(this.endpoints.stats);
            
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            return await response.json();
        } catch (error) {
            console.error('Error al obtener estadísticas:', error);
            throw error;
        }
    }

    /**
     * Fuerza actualización de datos
     * @returns {Promise<Object>} Resultado de la actualización
     */
    async forceUpdate() {
        try {
            const response = await fetch(this.endpoints.update, { 
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                }
            });
            
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            return await response.json();
        } catch (error) {
            console.error('Error al forzar actualización:', error);
            throw error;
        }
    }

    /**
     * Verifica el estado de salud de la API
     * @returns {Promise<Object>} Estado de salud
     */
    async checkHealth() {
        try {
            const response = await fetch(this.endpoints.health);
            
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            return await response.json();
        } catch (error) {
            console.error('Error al verificar salud:', error);
            throw error;
        }
    }
}

export class DataManager {
    constructor(apiService) {
        this.apiService = apiService;
        this.currentData = null;
        this.lastUpdate = null;
    }

    /**
     * Carga datos de sismos
     * @returns {Promise<Object>} Datos cargados
     */
    async loadData() {
        try {
            this.currentData = await this.apiService.getSismos();
            this.lastUpdate = new Date();
            return this.currentData;
        } catch (error) {
            // Intentar datos de respaldo
            return await this.loadFallbackData();
        }
    }

    /**
     * Carga datos de respaldo
     * @returns {Promise<Object>} Datos de respaldo
     */
    async loadFallbackData() {
        try {
            // En caso de error, intentar obtener datos nuevamente
            this.currentData = await this.apiService.getSismos();
            this.lastUpdate = new Date();
            return this.currentData;
        } catch (error) {
            console.error('No se pudieron cargar datos de respaldo:', error);
            throw new Error('API no disponible');
        }
    }

    /**
     * Fuerza actualización de datos
     * @returns {Promise<Object>} Resultado de la actualización
     */
    async forceUpdate() {
        const result = await this.apiService.forceUpdate();
        if (result.success) {
            // Esperar un momento y recargar datos
            await new Promise(resolve => setTimeout(resolve, 1000));
            return await this.loadData();
        }
        throw new Error('Error al actualizar datos');
    }

    /**
     * Obtiene los datos actuales
     * @returns {Object|null} Datos actuales
     */
    getCurrentData() {
        return this.currentData;
    }

    /**
     * Verifica si hay datos cargados
     * @returns {boolean} True si hay datos
     */
    hasData() {
        return ValidationUtils.isValidEarthquakeData(this.currentData);
    }

    /**
     * Obtiene el número de sismos
     * @returns {number} Número de sismos
     */
    getEarthquakeCount() {
        return this.hasData() ? this.currentData.features.length : 0;
    }
}