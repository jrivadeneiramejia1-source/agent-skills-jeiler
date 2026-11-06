# Lecciones (errores aprendidos)

Cada una salió de una prueba real, no de suposiciones.

| Fecha | Qué pasó | Qué se aprendió |
|---|---|---|
| 2026-11-06 | `revisar_flujo.py` no detectaba el token de Telegram dentro de una dirección (`/bot123456789:TOKEN`). | Un patrón con `\b` antes del número falla porque `t` y `1` son del mismo tipo de carácter. El ejemplo malo hecho a propósito lo descubrió. Hay una prueba que lo cubre. |
| 2026-11-06 | `revisar_bot.py` daba por bueno un bot sin `secret_token` porque un comentario decía «poner secret_token». | Buscar texto en código sin quitar comentarios engaña. Ahora se quitan comentarios antes de buscar. |
| 2026-11-06 | `console.log(JSON.stringify(ctx.update))` no se detectaba (solo se miraba `update` suelto). | Hay que aceptar prefijos como `ctx.`. |
| 2026-11-06 | Sobre 2.061 flujos reales, 65 avisos de clave eran marcadores (`<YOUR_API_KEY>`, `$OPENAI_API_KEY`). | Probar con datos reales baja los falsos positivos: bajaron a 22. Un revisor que grita por todo se deja de usar. |
| 2026-11-06 | `crear-agente` (de terceros) tenía una descripción que un lector de YAML estricto rechaza. | Probar los encabezados con un lector de YAML de verdad, no solo mirarlos. Está en `tests/`. |
| 2026-11-06 | `README.md` y `CLAUDE.md` eran los de Vercel, en inglés, y `CLAUDE.md` era un enlace a `AGENTS.md`. | Un Claude que abre el repo lee `CLAUDE.md` primero: ahí van las reglas de Jeiler. Lo de Vercel quedó en `docs/`. |
| 2026-11-06 | Mi bot de Telegram «bueno» daba 500 si Telegram fallaba al contestar, y yo había escrito `bot.catch` pensando que lo arreglaba. | Probarlo en un Worker real mostró que con webhooks `bot.catch` no se usa (grammY deja pasar el error). Se arregló con `try/catch` alrededor del webhook, y se midió. |
| 2026-11-06 | Mi bot de WhatsApp «bueno» daba 500 con un cuerpo roto pero bien firmado (`JSON.parse` sin protección). | Un probador que escribe al bot encuentra lo que un revisor de código no ve. Ahora devuelve 400. |
| 2026-11-06 | `flujo-bueno.json` mezclaba el formato nuevo del nodo IF con `typeVersion` 1. | Una segunda herramienta (valn8n) con otra mirada destapó un fallo de mi ejemplo. Conviene tener dos opiniones. |
| 2026-11-06 | `pkill workerd` apagó también los otros bots de prueba. | Usar un puerto distinto para cada bot y no matar procesos en bloque. |
| 2026-11-06 | Al activarse los flujos heredados de Vercel, «Agent Skills Discovery» falló: `crear-agente` tenía una descripción de 1.166 caracteres (máximo 1.024) y pesa 2,1 MB (el script admite 1 MB). | Las skills de terceros también deben cumplir la especificación. Una prueba ahora revisa nombre y descripción de las 48 skills; lo del tamaño queda para decidir. |
| 2026-11-06 | Mi arreglo anterior de `crear-agente` (bloque `>-`) arregló el YAML pero no el largo. | Probar con la **misma herramienta que usará el repo** (aquí el script de descubrimiento), no solo con un lector de YAML. |
| 2026-11-06 | El flujo heredado «Agent Skills Discovery» seguía fallando por el tamaño de `crear-agente`. | Jeiler decidió desactivarlo (renombrado `.yml.desactivado`, reversible). Un flujo heredado que no se usa y falla solo crea ruido. |
