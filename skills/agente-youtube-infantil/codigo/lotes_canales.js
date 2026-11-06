// ARMAR LOTES DE CANALES
// De los videos con estadísticas saca los canales (sin repetir) y los agrupa de 50 en 50.
const canales = new Set();
for (const it of $input.all()) {
  const j = it.json || {};
  if (j.error || !Array.isArray(j.items)) continue;
  for (const v of j.items) {
    const c = v && v.snippet && v.snippet.channelId;
    if (typeof c === 'string' && /^[A-Za-z0-9_-]{10,40}$/.test(c)) canales.add(c);
  }
}
const lista = [...canales];
const lotes = [];
for (let i = 0; i < lista.length; i += 50) {
  lotes.push({ json: { ids: lista.slice(i, i + 50).join(',') } });
}
if (!lotes.length) return [{ json: { ids: '' } }];
return lotes;
