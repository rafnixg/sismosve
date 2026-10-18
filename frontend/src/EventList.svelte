<!--
Copyright (C) 2025-2026 Rafnix Guzman (@rafnixg).
SPDX-License-Identifier: AGPL-3.0-only
Additional author-attribution term under section 7(b): see repository-root NOTICE.
-->
<script lang="ts">
  import { formatTime, hasCoordinates, magnitudeClass, type Earthquake } from './data';
  let { events, selected, onselect }: { events: Earthquake[]; selected: string | null; onselect: (id: string) => void } = $props();
  let list: HTMLOListElement;
  $effect(() => {
    if (selected && list) {
      const button = [...list.querySelectorAll<HTMLButtonElement>('[data-event]')].find(el => el.dataset.event === selected);
      if (!button) return;
      const row = button.getBoundingClientRect();
      const viewport = list.getBoundingClientRect();
      const top = viewport.top + list.clientTop;
      const bottom = top + list.clientHeight;
      // Only scroll the list: scrollIntoView would also move the page away
      // from the map when the two panels are stacked on mobile.
      if (row.top < top) list.scrollTo({ top: list.scrollTop + row.top - top, behavior: 'instant' });
      else if (row.bottom > bottom) list.scrollTo({ top: list.scrollTop + row.bottom - bottom, behavior: 'instant' });
    }
  });
</script>
<section class="event-panel" aria-labelledby="events-heading">
  <div class="list-heading"><h2 id="events-heading">Sismos recientes</h2><span>{events.length} registros</span></div>
  <ol class="event-list" bind:this={list}>
    {#each events as event (event.id)}
      <li><button class="event-row" class:selected={selected === event.id} data-event={event.id} aria-pressed={selected === event.id} onclick={() => onselect(event.id)}>
        <span class="magnitude {magnitudeClass(event.magnitude)}"><small>Magnitud</small>{Number.isFinite(event.magnitude) ? event.magnitude.toFixed(1) : '—'}</span>
        <span class="event-copy"><strong>{event.feature.properties.addressFormatted}</strong><span>{event.feature.properties.date} · {formatTime(event.feature.properties.time)}</span><span>Profundidad: {event.feature.properties.depth}</span>
          {#if selected === event.id}<span>{event.latitude}°, {event.longitude}° · {event.feature.properties.country}</span>{/if}
          {#if !hasCoordinates(event)}<span>Ubicación no disponible en el mapa</span>{/if}
        </span>
      </button></li>
    {:else}<li class="empty-state"><h3>No hay sismos para mostrar</h3><p>Prueba con otra magnitud o amplía el rango de fechas.</p></li>{/each}
  </ol>
</section>
