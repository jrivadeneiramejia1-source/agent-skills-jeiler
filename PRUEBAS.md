# Qué se probó de verdad (2026-11-04)

Solo se listan las skills originales de este repo. Las demás son copias de terceros: solo se revisó que sean válidas y seguras (ver `SEGURIDAD.md`).

| Skill | Estado | Qué se probó |
|---|---|---|
| **plantillas-n8n** | Probada en tarea real | Se clonó la biblioteca (2.061 flujos, todos legibles) y se probó el script de limpieza y la búsqueda de claves. Se descubrió que la biblioteca trae 217 flujos activos, 136 con `pinData`, 286 con correos escritos y 4 con algo con forma de clave real; el script limpiaba lo primero pero no lo último, y se agregó el paso de búsqueda de claves. |
| **seguridad-agentes** | Solo activación | Se abrió sola en 3 de 3 frases (Sonnet 5.5; con Haiku, 0 de 3). No se probó revisando un agente real. |
| **apis-gratis** | Solo activación | Se abrió sola en 3 de 3 frases (Haiku). Sus tablas de límites y precios se verifican al final contra las páginas oficiales. |
| **bot-telegram** | Probada en local | Se abrió sola en 3 de 3 frases (Haiku). El Worker del esqueleto corrió en el motor local de Cloudflare (`wrangler dev`): sin clave secreta o con una mala da 401, un usuario fuera de la lista no recibe respuesta y uno permitido dispara el envío. **No se probó** publicado en Cloudflare ni con un Telegram real (necesita un token real). |
| **probar-prompts** | Solo activación y configuración | Se abrió sola en 2 de 3 frases (Haiku). La configuración de promptfoo se probó con un «modelo» de eco (sin llamar a ninguna IA); no se probó con un modelo real. |

## Sobre la «activación sola»
Es si Claude abre la skill por su cuenta cuando el usuario pide algo parecido. Con 10 skills de los tres repos cargadas a la vez, en 50 frases (30 que debían activarla y 20 que no) con Haiku: **activó la correcta en 20 de 30 y nunca una equivocada (0 de 20)**. Son pocas repeticiones, con un modelo distinto al de uso diario; sirve como señal, no como medida exacta.

## Sin probar en ninguna skill
Conexión real con Gmail, Drive, Telegram, WhatsApp o n8n (necesitan claves y no se piden ni se guardan aquí).
