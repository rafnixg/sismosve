/*
Copyright (C) 2025-2026 Rafnix Guzman (@rafnixg).
SPDX-License-Identifier: AGPL-3.0-only
Additional author-attribution term under section 7(b): see repository-root NOTICE.
*/
export interface Feature {
  type: string;
  geometry: { type: string; coordinates: number[]; marcador?: string };
  properties: { depth: string; value: string; addressFormatted: string; time: string;
    country: string; date: string; lat: string; long: string };
}
export interface Collection { type: string; features: Feature[] }
export interface Earthquake { id: string; feature: Feature; magnitude: number; date: string;
  timestamp: string; latitude: number; longitude: number }
export interface Filters { magnitude: string; start: string; end: string }

export function normalize(data: Collection): Earthquake[] {
  if (!data || !Array.isArray(data.features)) throw new Error('La respuesta no contiene registros válidos.');
  const occurrences = new Map<string, number>();
  return data.features.map(feature => {
    const p = feature.properties;
    const [day, month, year] = p.date.split('-');
    const date = `${year}-${month}-${day}`;
    const key = JSON.stringify([p.date, p.time, p.lat, p.long, p.value, p.depth, p.addressFormatted]);
    const occurrence = occurrences.get(key) ?? 0;
    occurrences.set(key, occurrence + 1);
    return { id: `${key}:${occurrence}`, feature, magnitude: Number(p.value), date,
      timestamp: `${date}T${p.time}`, latitude: p.lat.trim() ? Number(p.lat) : NaN,
      longitude: p.long.trim() ? Number(p.long) : NaN };
  }).sort((a, b) => b.timestamp.localeCompare(a.timestamp));
}
export function filterEvents(events: Earthquake[], filters: Filters) {
  return events.filter(e => (!filters.magnitude || e.magnitude >= Number(filters.magnitude)) &&
    (!filters.start || e.date >= filters.start) && (!filters.end || e.date <= filters.end));
}
export function hasCoordinates(e: Earthquake) {
  return Number.isFinite(e.latitude) && Number.isFinite(e.longitude) &&
    Math.abs(e.latitude) <= 90 && Math.abs(e.longitude) <= 180;
}
export function magnitudeClass(value: number) { return value >= 5 ? 'high' : value >= 4 ? 'medium' : 'low'; }
export function formatTime(time: string) {
  const [hours, minutes] = time.split(':');
  const hour = Number(hours);
  return Number.isFinite(hour) ? `${hour % 12 || 12}:${minutes} ${hour >= 12 ? 'p. m.' : 'a. m.'}` : 'Hora no disponible';
}
export async function request<T>(url: string, signal: AbortSignal, method = 'GET'): Promise<T> {
  const response = await fetch(url, { signal, method });
  if (!response.ok) throw new Error(`El servicio respondió con un error (${response.status}).`);
  return response.json();
}
