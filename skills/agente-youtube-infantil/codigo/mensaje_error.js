// MENSAJE DE ERROR
// Se activa cuando falla OTRO flujo (el que lo tenga como «Error workflow»). Arma un aviso corto para Telegram.
// ---------------------------------------------------------------------------
const CHAT_ID = 'REEMPLAZA-CON-TU-CHAT-ID';
// ---------------------------------------------------------------------------
const esc = (s) => String(s == null ? '' : s).replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
const e = $input.first().json || {};
const flujo = (e.workflow && e.workflow.name) || 'un flujo';
const nodo = e.execution && e.execution.lastNodeExecuted;
const motivo = e.execution && e.execution.error && e.execution.error.message;
const texto = '⚠️ <b>Falló ' + esc(flujo) + '</b>' + (nodo ? '\nNodo: ' + esc(nodo) : '') + (motivo ? '\nMotivo: ' + esc(String(motivo).slice(0, 300)) : '') +
  '\n\nMira el detalle en Executions (Ejecuciones) de n8n.';
return [{ json: { texto, chatId: CHAT_ID } }];
