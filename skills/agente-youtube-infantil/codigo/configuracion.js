// CONFIGURACIÓN DEL INVESTIGADOR — edita solo esta parte (entre las dos líneas de guiones).
// ---------------------------------------------------------------------------
const CHAT_ID = 'REEMPLAZA-CON-TU-CHAT-ID';            // tu número de chat de Telegram (te lo explica la guía)
const CONSULTAS = ['canciones infantiles', 'canciones para niños', 'cuentos infantiles', 'videos infantiles'];
const VENTANAS_DIAS = [3, 7, 30];                       // busca videos de los últimos 3, 7 y 30 días
const MAX_POR_BUSQUEDA = 25;                            // cuántos videos pide por búsqueda (máximo 50)
// ---------------------------------------------------------------------------
// Cada combinación consulta × ventana es UNA búsqueda en la API de YouTube (1 de las 100 gratis al día).
// Con 4 consultas y 3 ventanas son 12 búsquedas por corrida.
const ahora = Date.now();
const trabajos = [];
for (const q of CONSULTAS) {
  for (const dias of VENTANAS_DIAS) {
    trabajos.push({
      json: {
        q,
        dias,
        publishedAfter: new Date(ahora - dias * 86400000).toISOString(),
        maxResults: Math.min(Math.max(Number(MAX_POR_BUSQUEDA) || 25, 1), 50),
        chatId: CHAT_ID,
      },
    });
  }
}
return trabajos;
