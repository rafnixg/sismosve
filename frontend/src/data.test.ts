/*
Copyright (C) 2025-2026 Rafnix Guzman (@rafnixg).
SPDX-License-Identifier: AGPL-3.0-only
Additional author-attribution term under section 7(b): see repository-root NOTICE.
*/
import { describe, it, expect } from 'vitest';
import { normalize, filterEvents, hasCoordinates, formatTime, request, type Collection } from './data';
import { vi } from 'vitest';

const fixture: Collection = { type: 'sismos', features: [
  { type: 'Sismo', geometry: { type: 'Point', coordinates: [-66, 8] }, properties: { depth: '10 km', value: '3.0', addressFormatted: 'Caracas', time: '09:05', country: 'Venezuela', date: '01-02-2026', lat: '8', long: '-66' } },
  { type: 'Sismo', geometry: { type: 'Point', coordinates: [-67, 9] }, properties: { depth: '20 km', value: '5.1', addressFormatted: 'Maracay', time: '13:10', country: 'Venezuela', date: '03-02-2026', lat: '9', long: '-67' } },
] };
describe('earthquake data', () => {
  it('accepts empty collections but rejects missing features', () => {
    expect(normalize({ type: 'sismos', features: [] })).toEqual([]);
    expect(() => normalize({} as Collection)).toThrow();
  });
  it('sorts by source date and retains identity when the input order changes', () => {
    const sorted = normalize(fixture);
    expect(sorted[0].feature.properties.addressFormatted).toBe('Maracay');
    expect(normalize({ ...fixture, features: [...fixture.features].reverse() }).map(e => e.id)).toEqual(sorted.map(e => e.id));
  });
  it('combines magnitude and inclusive date boundaries', () => {
    const events = normalize(fixture);
    expect(filterEvents(events, { magnitude: '4', start: '2026-02-03', end: '2026-02-03' })).toEqual([events[0]]);
    expect(filterEvents(events, { magnitude: '', start: '', end: '2026-02-01' })).toEqual([events[1]]);
    expect(filterEvents(events, { magnitude: '6', start: '', end: '' })).toEqual([]);
  });
  it('keeps invalid coordinates in the dataset but excludes them from map eligibility', () => {
    const event = normalize(fixture)[0];
    expect(hasCoordinates(event)).toBe(true);
    expect(hasCoordinates({ ...event, latitude: NaN })).toBe(false);
    expect(hasCoordinates({ ...event, longitude: 181 })).toBe(false);
  });
  it('formats midnight, noon and afternoon without timezone conversion', () => {
    expect(formatTime('00:05')).toBe('12:05 a. m.');
    expect(formatTime('12:05')).toBe('12:05 p. m.');
    expect(formatTime('23:05')).toBe('11:05 p. m.');
  });
  it('rejects HTTP failures instead of treating error bodies as data', async () => {
    vi.stubGlobal('fetch', vi.fn().mockResolvedValue({ ok: false, status: 503 }));
    await expect(request('/api/sismos', new AbortController().signal)).rejects.toThrow('503');
    vi.unstubAllGlobals();
  });
});
