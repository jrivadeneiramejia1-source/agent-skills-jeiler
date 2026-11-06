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
