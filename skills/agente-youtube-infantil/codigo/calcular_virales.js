// CALCULAR VIRALES
// Ordena los videos por cuánto superaron el promedio del RESTO de videos de su propio canal
// ("múltiplo"), para que un canal grande no gane solo por ser grande. Es una pista, no una garantía.
// ---------------------------------------------------------------------------
const MIN_VISTAS = 1000;          // ignora videos con menos vistas
const MIN_VIDEOS_CANAL = 5;       // el canal necesita al menos 5 videos para que su promedio signifique algo
const MIN_MULTIPLO = 2;           // solo videos que superaron al menos 2 veces el promedio de su canal
const TOP = 5;                    // cuántos muestra por ventana de tiempo
const VENTANAS = [
  { dias: 3, nombre: 'Últimos 3 días' },
  { dias: 7, nombre: 'Últimos 7 días' },
  { dias: 30, nombre: 'Últimos 30 días' },
];
// ---------------------------------------------------------------------------
const esc = (s) => String(s == null ? '' : s).replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
const num = (n) => Math.round(Number(n)).toString().replace(/\B(?=(\d{3})+(?!\d))/g, '.');
const dec = (n) => (Math.round(n * 10) / 10).toString().replace('.', ',');
const duracion = (iso) => {
  const m = /^PT(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?$/.exec(String(iso || ''));
  if (!m) return 0;
  return (Number(m[1] || 0) * 3600) + (Number(m[2] || 0) * 60) + Number(m[3] || 0);
};
const mmss = (seg) => {
  const h = Math.floor(seg / 3600), m = Math.floor((seg % 3600) / 60), s = seg % 60;
  return (h ? h + ':' + String(m).padStart(2, '0') : m) + ':' + String(s).padStart(2, '0');
};

const chatId = ($('Configuración').first().json || {}).chatId;
const ahora = Date.now();

// Canales: id -> promedio de vistas del RESTO de sus videos (sin contar el que estamos evaluando)
const canales = new Map();
for (const it of $input.all()) {
  const j = it.json || {};
  if (j.error || !Array.isArray(j.items)) continue;
  for (const c of j.items) {
    const st = (c && c.statistics) || {};
    canales.set(c.id, {
      vistas: Number(st.viewCount),
      videos: Number(st.videoCount),
      suscriptores: st.hiddenSubscriberCount ? null : Number(st.subscriberCount),
      nombre: (c.snippet && c.snippet.title) || '',
    });
  }
}

const candidatos = [];
const vistos = new Set();
let revisados = 0;
for (const it of $('Estadísticas de videos').all()) {
  const j = it.json || {};
  if (j.error || !Array.isArray(j.items)) continue;
  for (const v of j.items) {
    if (!v || !v.id || vistos.has(v.id)) continue;
    vistos.add(v.id);
    revisados++;
    const sn = v.snippet || {};
    if (sn.liveBroadcastContent && sn.liveBroadcastContent !== 'none') continue;   // sin directos
    const vistas = Number((v.statistics || {}).viewCount);
    const canal = canales.get(sn.channelId);
    if (!Number.isFinite(vistas) || vistas < MIN_VISTAS || !canal) continue;
    if (!Number.isFinite(canal.videos) || canal.videos < MIN_VIDEOS_CANAL || !Number.isFinite(canal.vistas)) continue;
    const base = (canal.vistas - vistas) / (canal.videos - 1);          // promedio del resto de videos
    if (!(base > 0)) continue;
    const multiplo = vistas / base;
    const publicado = Date.parse(sn.publishedAt);
    if (!Number.isFinite(publicado)) continue;
    const edadDias = (ahora - publicado) / 86400000;
    if (edadDias < 0) continue;
    const ventana = VENTANAS.find((w) => edadDias <= w.dias);
    if (!ventana || multiplo < MIN_MULTIPLO) continue;
    candidatos.push({
      id: v.id, titulo: sn.title || '(sin título)', canal: sn.channelTitle || canal.nombre, vistas, multiplo,
      edadDias, ventana: ventana.nombre, seg: duracion((v.contentDetails || {}).duration),
    });
  }
}

const bloques = [];
let mostrados = 0;
for (const w of VENTANAS) {
  const lista = candidatos.filter((c) => c.ventana === w.nombre).sort((a, b) => b.multiplo - a.multiplo).slice(0, TOP);
  if (!lista.length) continue;
  const lineas = lista.map((c, i) => {
    mostrados++;
    const hace = c.edadDias < 1 ? 'hoy' : 'hace ' + Math.floor(c.edadDias) + ' d';
    return (i + 1) + '. <b>' + esc(c.titulo) + '</b>\n   ' + esc(c.canal) + ' · ' + hace + ' · ' + num(c.vistas) + ' vistas · ×' + dec(c.multiplo) +
      ' su promedio' + (c.seg ? ' · ' + mmss(c.seg) : '') + '\n   https://youtu.be/' + c.id;
  });
  bloques.push('<b>' + w.nombre + '</b>\n' + lineas.join('\n'));
}

let texto;
if (!mostrados) {
  texto = 'Hoy no encontré videos que superen ' + MIN_MULTIPLO + ' veces el promedio de su canal (revisé ' + revisados + ' videos).';
} else {
  texto = '🔎 <b>Videos infantiles que están funcionando</b> (revisé ' + revisados + ')\n\n' + bloques.join('\n\n') +
    '\n\nEl «×» compara cada video con el promedio del RESTO de videos de su canal: es una pista, no una garantía. ' +
    'Úsalo para aprender la fórmula (tema, gancho, estructura), nunca para copiar su personaje, guion, imágenes ni música.';
  while (texto.length > 3900 && bloques.length > 1) {      // Telegram acepta hasta 4096 caracteres
    bloques.pop();
    texto = '🔎 <b>Videos infantiles que están funcionando</b> (recortado)\n\n' + bloques.join('\n\n');
  }
}
return [{ json: { texto, chatId, revisados, mostrados } }];
