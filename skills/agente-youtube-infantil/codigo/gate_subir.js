// SOLO TU CHAT Y /subir N
// 1) Descarta (en silencio) cualquier mensaje que no venga de TU chat: el bot de Telegram es público.
// 2) Descarta mensajes viejos (Telegram reentrega los pendientes cuando vuelve la conexión).
// 3) Solo entiende "/subir 1", "/subir 2" o "/subir 3". La ruta se arma con una carpeta fija + ese dígito:
//    nada de lo que escriba la persona entra en una ruta ni en un comando.
// ---------------------------------------------------------------------------
const CHAT_AUTORIZADO = 'REEMPLAZA-CON-TU-CHAT-ID';
const BASE = 'C:\\Users\\TU-USUARIO\\.n8n-files\\opciones';   // dentro de ~/.n8n-files, que n8n 2.x permite por defecto
// ---------------------------------------------------------------------------
const trigger = $input.first().json || {};
const msg = trigger.message || {};
const chatId = msg.chat ? msg.chat.id : undefined;
if (String(chatId) !== CHAT_AUTORIZADO) return [];                    // mensaje ajeno: no se responde nada

const fecha = Number(msg.date);
if (fecha > 0 && (Date.now() / 1000 - fecha) > 600) return [];        // más de 10 minutos de antigüedad

const texto = String(msg.text || '').trim();
const m = /^\/subir(?:@\w+)?\s+([1-3])$/.exec(texto);
if (!m) {
  return [{ json: { valido: false, chatId, respuesta: 'Para subir un video escribe: /subir 1, /subir 2 o /subir 3' } }];
}
const n = m[1];
return [{
  json: {
    valido: true,
    chatId,
    opcion: n,
    rutaMeta: BASE + '\\' + n + '\\publicacion.json',
    rutaVideo: BASE + '\\' + n + '\\video.mp4',
  },
}];
