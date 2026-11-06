// VALIDAR DATOS
// Lee publicacion.json de la carpeta elegida y comprueba título, descripción y etiquetas ANTES de subir.
// Lo importante lo fija este código y NO el archivo ni una IA: el video se sube siempre en PRIVADO,
// siempre marcado «para niños», en español. Aunque publicacion.json diga otra cosa, se ignora.
// ---------------------------------------------------------------------------
const MAX_TITULO = 100;                 // límite de YouTube
const MAX_DESCRIPCION_BYTES = 4800;     // YouTube acepta 5000 bytes; se deja margen
const MAX_ETIQUETAS_CARACTERES = 450;   // YouTube acepta 500 en total
const MAX_ETIQUETAS = 20;
// ---------------------------------------------------------------------------
const previo = $('Solo tu chat y /subir N').first().json;
const falla = (motivo) => [{ json: { ok: false, chatId: previo.chatId, respuesta: 'No subí nada. ' + motivo } }];

let datos;
try {
  const buf = await this.helpers.getBinaryDataBuffer(0, 'meta');
  datos = JSON.parse(buf.toString('utf8'));
} catch (e) {
  return falla('No pude leer publicacion.json de la carpeta ' + previo.opcion + ' (¿existe y es un JSON válido?).');
}
if (!datos || typeof datos !== 'object' || Array.isArray(datos)) return falla('publicacion.json debe ser un objeto con titulo, descripcion y etiquetas.');

const titulo = typeof datos.titulo === 'string' ? datos.titulo.trim() : '';
if (!titulo) return falla('Falta el «titulo» en publicacion.json.');
if (titulo.length > MAX_TITULO) return falla('El título tiene ' + titulo.length + ' caracteres; el máximo es ' + MAX_TITULO + '.');
if (/[<>]/.test(titulo)) return falla('El título no puede llevar los símbolos < o >.');

const descripcion = typeof datos.descripcion === 'string' ? datos.descripcion.trim() : '';
if (!descripcion) return falla('Falta la «descripcion» en publicacion.json (créditos, fuentes y la frase de IA si aplica).');
if (Buffer.byteLength(descripcion, 'utf8') > MAX_DESCRIPCION_BYTES) return falla('La descripción es demasiado larga (máximo ' + MAX_DESCRIPCION_BYTES + ' bytes).');
if (/[<>]/.test(descripcion)) return falla('La descripción no puede llevar los símbolos < o >.');

const etiquetasIn = Array.isArray(datos.etiquetas) ? datos.etiquetas : [];
const etiquetas = etiquetasIn.map((t) => String(t == null ? '' : t).replace(/[,<>]/g, ' ').trim()).filter(Boolean);
if (etiquetas.length > MAX_ETIQUETAS) return falla('Hay ' + etiquetas.length + ' etiquetas; el máximo es ' + MAX_ETIQUETAS + '.');
const total = etiquetas.reduce((s, t) => s + t.length + 1, 0);
if (total > MAX_ETIQUETAS_CARACTERES) return falla('Las etiquetas suman demasiados caracteres (máximo ' + MAX_ETIQUETAS_CARACTERES + ').');

return [{
  json: {
    ok: true,
    chatId: previo.chatId,
    opcion: previo.opcion,
    titulo,
    descripcion,
    etiquetas: etiquetas.join(','),
    // Fijos, no se leen del archivo:
    privacidad: 'private',
    paraNinos: true,
    categoria: '24',
    idioma: 'es',
  },
}];
