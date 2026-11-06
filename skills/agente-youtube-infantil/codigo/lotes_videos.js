// ARMAR LOTES DE VIDEOS
// Junta los videos que devolvieron todas las búsquedas, quita los repetidos y los agrupa de 50 en 50
// (la API de YouTube acepta hasta 50 identificadores por consulta de estadísticas).
const ids = new Set();
let erroresBusqueda = 0;
for (const it of $input.all()) {
  const j = it.json || {};
  if (j.error || !Array.isArray(j.items)) { erroresBusqueda++; continue; }   // una búsqueda falló: se sigue con las demás
  for (const v of j.items) {
    const id = v && v.id && v.id.videoId;
    if (typeof id === 'string' && /^[A-Za-z0-9_-]{6,20}$/.test(id)) ids.add(id);
  }
}
const lista = [...ids].slice(0, 300);                   // tope de seguridad
const lotes = [];
for (let i = 0; i < lista.length; i += 50) {
  lotes.push({ json: { ids: lista.slice(i, i + 50).join(','), erroresBusqueda } });
}
if (!lotes.length) return [{ json: { ids: '', erroresBusqueda } }];
return lotes;
