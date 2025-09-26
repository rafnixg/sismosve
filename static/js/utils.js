/**
 * Funciones utilitarias para la aplicación SismosVE
 */

export class DateTimeUtils {
    /**
     * Convierte fecha DD-MM-YYYY y hora HH:MM a objeto Date
     * @param {string} date - Fecha en formato DD-MM-YYYY
     * @param {string} time - Hora en formato HH:MM
     * @returns {Date} Objeto Date
     */
    static parseDateTime(date, time) {
        try {
            const [day, month, year] = date.split('-');
            const [hours, minutes] = time.split(':');
            return new Date(year, month - 1, day, hours, minutes);
        } catch {
            return new Date(0);
        }
    }

    /**
     * Convierte tiempo de formato 24H a 12H
     * @param {string} time24 - Tiempo en formato 24H (HH:MM)
     * @returns {string} Tiempo en formato 12H (H:MM AM/PM)
     */
    static convertTo12Hour(time24) {
        try {
            const [hours, minutes] = time24.split(':');
            const hour24 = parseInt(hours, 10);
            const hour12 = hour24 === 0 ? 12 : hour24 > 12 ? hour24 - 12 : hour24;
            const ampm = hour24 >= 12 ? 'PM' : 'AM';
            return `${hour12}:${minutes} ${ampm}`;
        } catch {
            return time24; // Retorna el original si hay error
        }
    }

    /**
     * Obtiene el sismo más reciente de una lista
     * @param {Array} features - Lista de sismos
     * @returns {Object|null} Sismo más reciente
     */
    static getLatestEarthquake(features) {
        return features.reduce((latest, current) => {
            if (!latest) return current;
            
            const currentDateTime = this.parseDateTime(current.properties.date, current.properties.time);
            const latestDateTime = this.parseDateTime(latest.properties.date, latest.properties.time);
            
            return currentDateTime > latestDateTime ? current : latest;
        }, null);
    }
}

export class MagnitudeUtils {
    /**
     * Obtiene la clase CSS basada en la magnitud
     * @param {number} magnitude - Magnitud del sismo
     * @returns {string} Clase CSS
     */
    static getMagnitudeClass(magnitude) {
        if (magnitude >= 5.0) return 'high';
        if (magnitude >= 4.0) return 'medium';
        return 'low';
    }

    /**
     * Obtiene el estilo del marcador basado en la magnitud
     * @param {number} magnitude - Magnitud del sismo
     * @returns {Object} Objeto con color y radio
     */
    static getMarkerStyle(magnitude) {
        if (magnitude >= 5.0) {
            return { color: '#f44336', radius: 12 }; // Rojo - grande
        } else if (magnitude >= 4.0) {
            return { color: '#ff9800', radius: 10 }; // Naranja - mediano
        } else {
            return { color: '#4CAF50', radius: 8 };  // Verde - pequeño
        }
    }
}

export class FileUtils {
    /**
     * Descarga datos como archivo JSON
     * @param {Object} data - Datos a descargar
     * @param {string} filename - Nombre del archivo
     */
    static downloadJSON(data, filename) {
        const dataStr = JSON.stringify(data, null, 2);
        const dataBlob = new Blob([dataStr], { type: 'application/json' });
        
        const link = document.createElement('a');
        link.href = URL.createObjectURL(dataBlob);
        link.download = filename;
        link.click();
        
        URL.revokeObjectURL(link.href);
    }

    /**
     * Genera nombre de archivo con fecha actual
     * @param {string} prefix - Prefijo del archivo
     * @param {string} extension - Extensión del archivo
     * @returns {string} Nombre del archivo
     */
    static generateFilename(prefix, extension = 'json') {
        const today = new Date().toISOString().split('T')[0];
        return `${prefix}_${today}.${extension}`;
    }
}

export class ValidationUtils {
    /**
     * Valida si los datos de sismos son válidos
     * @param {Object} data - Datos a validar
     * @returns {boolean} True si los datos son válidos
     */
    static isValidEarthquakeData(data) {
        return data && 
               typeof data === 'object' && 
               Array.isArray(data.features) && 
               data.features.length > 0;
    }

    /**
     * Valida coordenadas
     * @param {number} lat - Latitud
     * @param {number} lng - Longitud
     * @returns {boolean} True si las coordenadas son válidas
     */
    static isValidCoordinates(lat, lng) {
        return !isNaN(lat) && !isNaN(lng) && 
               lat >= -90 && lat <= 90 && 
               lng >= -180 && lng <= 180;
    }
}