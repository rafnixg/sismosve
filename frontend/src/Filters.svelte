<!--
Copyright (C) 2025-2026 Rafnix Guzman (@rafnixg).
SPDX-License-Identifier: AGPL-3.0-only
Additional author-attribution term under section 7(b): see repository-root NOTICE.
-->
<script lang="ts">
  import type { Filters } from './data';
  let { filters, invalid }: { filters: Filters; invalid: boolean } = $props();
</script>
<form class="filters" onsubmit={e => e.preventDefault()} aria-label="Filtrar sismos">
  <label>Magnitud mínima<select bind:value={filters.magnitude}><option value="">Todas</option><option value="2">2,0</option><option value="3">3,0</option><option value="4">4,0</option><option value="5">5,0</option></select></label>
  <label>Desde<input type="date" bind:value={filters.start} aria-invalid={invalid} aria-describedby={invalid ? 'date-error' : undefined}></label>
  <label>Hasta<input type="date" bind:value={filters.end} aria-invalid={invalid} aria-describedby={invalid ? 'date-error' : undefined}></label>
  <button class="text-button" type="button" onclick={() => { filters.magnitude = ''; filters.start = ''; filters.end = ''; }}>Limpiar filtros</button>
  <p id="date-error" class="filter-error" aria-live="polite">{invalid ? 'La fecha inicial debe ser anterior o igual a la final.' : ''}</p>
</form>
