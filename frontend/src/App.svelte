<script lang="ts">
  import { onMount } from 'svelte';
  import MapView from './Map.svelte';
  import FiltersView from './Filters.svelte';
  import EventList from './EventList.svelte';
  import { normalize, filterEvents, request, type Collection, type Earthquake, type Filters } from './data';
  let events = $state<Earthquake[]>([]);
  let collection = $state<Collection | null>(null);
  let filters = $state<Filters>({ magnitude: '', start: '', end: '' });
  let selected = $state<string | null>(null);
  let loading = $state(false);
  let error = $state('');
  let queried = $state('');
  let updated = $state('');
  let controller: AbortController | undefined;
  const invalid = $derived(Boolean(filters.start && filters.end && filters.start > filters.end));
  const visible = $derived(invalid ? [] : filterEvents(events, filters));
  const maximum = $derived(visible.reduce((max, e) => Number.isFinite(e.magnitude) ? Math.max(max, e.magnitude) : max, -Infinity));
  $effect(() => { if (selected && !visible.some(e => e.id === selected)) selected = null; });
  async function load(force = false) {
    if (loading) return;
    controller = new AbortController(); const signal = controller.signal;
    loading = true; error = '';
    try {
      if (force) {
        const result = await request<{ success: boolean }>('/api/update', signal, 'POST');
        if (!result.success) throw new Error('FUNVISIS no pudo actualizar los registros. Inténtalo de nuevo más tarde.');
      }
      const data = await request<Collection>('/api/sismos', signal);
      const normalized = normalize(data);
      collection = data; events = normalized;
      queried = new Date().toLocaleTimeString('es-VE', { hour: 'numeric', minute: '2-digit', hour12: true });
      try {
        const status = await request<{ data: { last_update: string | null } }>('/api/status', signal);
        updated = status.data.last_update ? status.data.last_update.replace('T', ' ').slice(0, 19) : 'Sin actualización confirmada';
      } catch { updated = 'No disponible'; }
    } catch (e) {
      if (!(e instanceof DOMException && e.name === 'AbortError')) error = e instanceof Error ? e.message : 'No se pudieron cargar los datos.';
    } finally { loading = false; }
  }
  function download() {
    if (!collection) return;
    const blob = new Blob([JSON.stringify({ ...collection, features: visible.map(e => e.feature) }, null, 2)], { type: 'application/json' });
    const url = URL.createObjectURL(blob); const a = document.createElement('a');
    a.href = url; a.download = `sismos_${new Date().toISOString().slice(0, 10)}.json`; a.click();
    setTimeout(() => URL.revokeObjectURL(url), 1000);
  }
  onMount(() => {
    load(); const interval = setInterval(() => load(), 300000);
    return () => { clearInterval(interval); controller?.abort(); };
  });
</script>

<div class="toolbar">
  <div class="data-status" role="status" aria-live="polite"><i class="dot" class:loading></i>{loading ? 'Consultando registros…' : queried ? `Consultado a las ${queried}` : 'Preparando registros'}<small>Actualización automática cada 5 minutos</small></div>
  <div class="actions"><button disabled={loading} onclick={() => load()}>Recargar</button><button disabled={loading} onclick={() => load(true)}>Actualizar desde FUNVISIS</button><button class="primary" disabled={!collection || invalid} onclick={download}>Exportar JSON</button></div>
</div>
{#if error}<div class="error-banner" role="alert"><p>{error} {collection ? 'Se conservan los últimos datos consultados.' : 'Comprueba tu conexión e inténtalo de nuevo.'}</p><button disabled={loading} onclick={() => load()}>Reintentar</button></div>{/if}
<FiltersView {filters} {invalid}/>
<div class="summary" aria-label="Resumen de resultados">
  <div><strong>{visible.length}</strong><span>Sismos encontrados</span></div>
  <div><strong>{maximum > -Infinity ? maximum.toFixed(1) : '—'}</strong><span>Mayor magnitud</span></div>
  <div class="last-event"><strong>{visible[0]?.feature.properties.date ?? '—'}</strong><span>Último sismo en los resultados</span></div>
</div>
<div class="workspace" aria-busy={loading}><MapView events={visible} {selected} onselect={id => selected = id}/><EventList events={visible} {selected} onselect={id => selected = id}/></div>
<p class="source-note">Datos de FUNVISIS · Fechas y horas según la fuente. Última actualización del servicio: {updated || 'Consultando…'}. Los colores indican magnitud, no intensidad percibida.</p>
