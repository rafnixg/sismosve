<!--
Copyright (C) 2025-2026 Rafnix Guzman (@rafnixg).
SPDX-License-Identifier: AGPL-3.0-only
Additional author-attribution term under section 7(b): see repository-root NOTICE.
-->
<script lang="ts">
  import { formatTime, magnitudeClass, type Earthquake } from './data';

  let { events, total, filtered, loading, invalid, failed }: {
    events: Earthquake[];
    total: number | null;
    filtered: boolean;
    loading: boolean;
    invalid: boolean;
    failed: boolean;
  } = $props();

  const ready = $derived(total !== null && !invalid);
  const latest = $derived(ready ? events[0] : undefined);
  const maximum = $derived(events.reduce((max, event) =>
    Number.isFinite(event.magnitude) ? Math.max(max, event.magnitude) : max, -Infinity));
  const hasMagnitude = $derived(ready && Number.isFinite(maximum));
  const unavailable = $derived(invalid ? 'Revisa el rango de fechas' :
    loading && total === null ? 'Consultando registros…' :
    total === null ? 'Datos no disponibles' : 'Sin resultados');
  const countContext = $derived(!ready ? unavailable : failed ? 'Últimos datos disponibles' :
    filtered ? `de ${total} registros consultados` : 'En los datos consultados');

  function readableDate(date: string) {
    const [day, month, year] = date.split('-');
    const months = ['ene', 'feb', 'mar', 'abr', 'may', 'jun', 'jul', 'ago', 'sep', 'oct', 'nov', 'dic'];
    return months[Number(month) - 1] ? `${Number(day)} ${months[Number(month) - 1]} ${year}` : date;
  }
</script>

<section class="results-summary" aria-label="Resumen de resultados" aria-busy={loading}>
  <dl class="summary-metrics">
    <div class="summary-metric">
      <dt>Sismos encontrados</dt>
      <dd class="summary-value">{ready ? events.length : '—'}</dd>
      <dd class="summary-context" aria-live="polite" aria-atomic="true">
        {#if ready}<span class="visually-hidden">{events.length} sismos encontrados. </span>{/if}{countContext}
      </dd>
    </div>
    <div class="summary-metric">
      <dt>Mayor magnitud</dt>
      <dd class="summary-value" class:low={hasMagnitude && magnitudeClass(maximum) === 'low'} class:medium={hasMagnitude && magnitudeClass(maximum) === 'medium'} class:high={hasMagnitude && magnitudeClass(maximum) === 'high'}>
        {#if hasMagnitude}<span class="summary-unit" aria-hidden="true">M</span> {maximum.toFixed(1)}{:else}—{/if}
      </dd>
      <dd class="summary-context">{hasMagnitude ? 'En los resultados visibles' : unavailable}</dd>
    </div>
    <div class="summary-metric summary-latest">
      <dt>Último sismo</dt>
      <dd class="summary-value summary-date">
        {#if latest}
          <time datetime={`${latest.date}T${latest.feature.properties.time}`}>
            <span>{readableDate(latest.feature.properties.date)}</span>
            <span class="summary-hour">{formatTime(latest.feature.properties.time)}</span>
          </time>
        {:else}—{/if}
      </dd>
      <dd class="summary-context summary-location" title={latest?.feature.properties.addressFormatted}>
        {latest ? latest.feature.properties.addressFormatted : unavailable}
      </dd>
    </div>
  </dl>
</section>
