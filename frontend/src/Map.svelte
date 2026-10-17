<script lang="ts">
  import { onMount } from 'svelte';
  import L from 'leaflet';
  import { hasCoordinates, magnitudeClass, formatTime, type Earthquake } from './data';
  let { events, selected, onselect }: { events: Earthquake[]; selected: string | null; onselect: (id: string) => void } = $props();
  let container: HTMLDivElement;
  let map = $state<L.Map>();
  let layers: L.LayerGroup;
  let markers = new Map<string, L.CircleMarker>();
  let tileError = $state(false);
  onMount(() => {
    const instance = L.map(container).setView([8, -66], 6);
    layers = L.layerGroup().addTo(instance);
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
      attribution: '© <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>', maxZoom: 18,
    }).on('tileerror', () => tileError = true).addTo(instance);
    L.control.scale({ imperial: false }).addTo(instance);
    const observer = new ResizeObserver(() => instance.invalidateSize());
    observer.observe(container);
    map = instance;
    return () => { observer.disconnect(); instance.remove(); };
  });
  $effect(() => {
    if (!map || !layers) return;
    layers.clearLayers(); markers.clear();
    const css = getComputedStyle(document.documentElement);
    const bounds: L.LatLngExpression[] = [];
    for (const event of events.filter(hasCoordinates)) {
      const color = css.getPropertyValue(`--color-${magnitudeClass(event.magnitude)}`).trim();
      const marker = L.circleMarker([event.latitude, event.longitude], {
        radius: event.magnitude >= 5 ? 12 : event.magnitude >= 4 ? 9 : 6,
        color, fillColor: color, fillOpacity: .65, weight: 2,
      }).addTo(layers);
      const popup = document.createElement('div');
      const heading = document.createElement('strong');
      heading.textContent = `M ${event.magnitude.toFixed(1)} · ${event.feature.properties.addressFormatted}`;
      const detail = document.createElement('p');
      detail.textContent = `${event.feature.properties.date} · ${formatTime(event.feature.properties.time)} · ${event.feature.properties.depth}`;
      popup.append(heading, detail);
      marker.bindPopup(popup).on('click', () => onselect(event.id));
      markers.set(event.id, marker); bounds.push([event.latitude, event.longitude]);
    }
    if (bounds.length) map.fitBounds(L.latLngBounds(bounds), { padding: [36, 36], maxZoom: 9 });
    else map.setView([8, -66], 6);
  });
  $effect(() => {
    if (!map) return;
    void events;
    const marker = selected ? markers.get(selected) : undefined;
    if (marker) { map.panTo(marker.getLatLng(), { animate: !matchMedia('(prefers-reduced-motion: reduce)').matches }); marker.openPopup(); }
    else map.closePopup();
  });
</script>

<section class="map-panel" aria-label="Mapa de sismos en Venezuela">
  <div class="map-heading"><h2>Actividad sísmica</h2><span>Venezuela y alrededores</span></div>
  <div class="map-canvas" bind:this={container}></div>
  <div class="map-legend" aria-label="Leyenda de magnitudes"><span><i class="dot low"></i>Menor de 4</span><span><i class="dot medium"></i>4 a 4,9</span><span><i class="dot high"></i>5 o más</span></div>
  {#if tileError}<p class="map-notice">No se pudo cargar parte del mapa. Consulta los registros en la lista.</p>{/if}
</section>
