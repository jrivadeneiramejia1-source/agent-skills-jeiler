# Qué se probó de verdad (2026-11-04, actualizado el 2026-11-06)

Solo se listan las skills originales de este repo. Las demás son copias de terceros: solo se revisó que sean válidas y seguras (ver `SEGURIDAD.md`).

| Skill | Estado | Qué se probó |
|---|---|---|
| **plantillas-n8n** | Probada en tarea real | Se clonó la biblioteca (2.061 flujos, todos legibles) y se probó el script de limpieza y la búsqueda de claves. Se descubrió que la biblioteca trae 217 flujos activos, 136 con `pinData`, 286 con correos escritos y 4 con algo con forma de clave real; el script limpiaba lo primero pero no lo último, y se agregó el paso de búsqueda de claves. |
| **seguridad-agentes** | Solo activación | Se abrió sola en 3 de 3 frases (Sonnet 5.5; con Haiku, 0 de 3). No se probó revisando un agente real. |
| **apis-gratis** | Solo activación | Se abrió sola en 3 de 3 frases (Haiku). Sus tablas de límites y precios se verifican al final contra las páginas oficiales. |
| **bot-telegram** | Probada en local | Se abrió sola en 3 de 3 frases (Haiku). El Worker del esqueleto corrió en el motor local de Cloudflare (`wrangler dev`): sin clave secreta o con una mala da 401, un usuario fuera de la lista no recibe respuesta y uno permitido dispara el envío. **No se probó** publicado en Cloudflare ni con un Telegram real (necesita un token real). |
| **probar-prompts** | Solo activación y configuración | Se abrió sola en 2 de 3 frases (Haiku). La configuración de promptfoo se probó con un «modelo» de eco (sin llamar a ninguna IA); no se probó con un modelo real. |

## Revisores automáticos nuevos (2026-11-06)
| Qué | Cómo | Resultado |
|---|---|---|
| **revisar-flujo-n8n** (`revisar_flujo.py`) | Ejemplo bueno y ejemplo malo hechos a propósito, 7 cambios puntuales (quitar el filtro de usuario, abrir un webhook, agregar `pinData`…), entradas rotas | Bueno: 0 hallazgos. Malo: 14 hallazgos, 5 graves, salida 1. Cada cambio dispara su regla. Archivo inexistente, JSON roto o «no es un flujo»: salida 2. El informe no contiene valores secretos. |
| Mismo revisor sobre **2.061 flujos reales** (biblioteca pública `Zie619/n8n-workflows`) | Se leyeron todos (0 ilegibles, 1,3 s) | 304 flujos con algún hallazgo grave. Primera pasada: 65 avisos F02 y 9 F01, muchos eran marcadores como `<YOUR_API_KEY>`; se ajustó y bajaron a 22 y 5 (las que quedan parecen claves reales o falta revisarlas a mano). 285 webhooks sin autenticación, 86 disparadores de Telegram sin filtro, 1.850 sin manejo de errores. |
| **revisar_bot.py** (en `seguridad-agentes`) | 4 bots de ejemplo (Telegram y WhatsApp, bueno y malo), carpetas de prueba con `.env` con y sin `.gitignore`, firma sin comparación segura, `eval` | Buenos: sin hallazgos graves ni medios. Malos: Telegram 4 graves, WhatsApp 1 grave más 3 medios. |
| Verificación de firma de WhatsApp (`bot-whatsapp-bueno/src/firma.mjs`) | Node 22, HMAC-SHA256 real: firma buena, cuerpo alterado, otro secreto, encabezado ausente, sin prefijo, hex corto, hex inválido, secreto vacío | 8 de 8 bien. |
| Pruebas del repo (`tests/`) | `python -I -m unittest discover -s tests`: grupos apuntan a skills que existen, encabezados YAML válidos, sin zips repetidos, sin correos ni teléfonos reales, documentos con `python` y no `python3`, revisores | 25 pruebas, todas pasan. |
| Las pruebas detectan fallas | Se rompió a propósito la regla F07 y, aparte, el filtro de comentarios y la regla de `secret_token` | En cada caso fallaron 2 pruebas (bien) y se restauró. |

## Herramientas nuevas y pruebas en vivo (2026-11-06, segunda ronda)
| Qué | Cómo | Resultado |
|---|---|---|
| **probar_webhook.py** (nuevo, en `seguridad-agentes`) | Se le manda mensajes falsos a un bot **corriendo**. Contra Workers reales locales (`wrangler dev` 4.158.0, grammY 1.46.0, claves inventadas) | Telegram bueno: 7 de 7. WhatsApp bueno: 11 de 11. Telegram malo (sin clave, sin lista): 0 de 7. WhatsApp malo (sin firma): 4 de 11. |
| Lo que encontró en mis propios ejemplos | Telegram: si Telegram fallaba al contestar, el Worker daba **500** (Telegram reintenta). `bot.catch` no lo arregla con webhooks (se probó): se arregló con `try/catch` alrededor del webhook. WhatsApp: cuerpo roto pero bien firmado daba 500; ahora 400. | Corregidos en `bot-telegram-bueno`, `bot-whatsapp-bueno` y en el esqueleto de `bot-telegram`. |
| Pruebas del probador | `tests/test_probar_webhook.py`: bots de mentira (Python) correctos y malos; direcciones remotas sin permiso → salida 2; bot apagado → salida 2 con mensaje claro; argumentos incompletos | 7 pruebas pasan. |
| **valn8n 0.1.1** (herramienta de terceros, MIT) sobre mis ejemplos de n8n | Revisión de su código (0 usos de red ni de ejecución), instalada en un entorno aparte | Complementa a `revisar_flujo.py` (estructura, no seguridad). Descubrió un fallo de mi `flujo-bueno.json` (IF con `typeVersion` 1 y formato nuevo): corregido. Ver `skills/revisar-flujo-n8n/references/herramientas.md`. |
| **actionlint 1.7.12 y zizmor 1.32.0** (MIT) sobre los flujos de este repo | `.github/workflows/` heredados de Vercel y el nuevo `pruebas.yml` | Nuevo `pruebas.yml`: 0 hallazgos con ambos (incluso con zizmor en modo pedante). Los heredados de Vercel: actionlint 0; zizmor 5 `unpinned-uses`, 3 `artipacked` y 1 `excessive-permissions` (**no se tocaron**: son de Vercel). |
| gitleaks sobre el **historial completo** (287 commits) | `gitleaks detect --log-opts=--all` | 6 hallazgos, todos ejemplos ficticios: los 5 de antes y un texto viejo de `SEGURIDAD.md` que citaba el ejemplo (ya reescrito). Ninguno real. |
| Pruebas del repo | `python -I -m unittest discover -s tests` | 32 pruebas pasan. |

### Qué no se probó (revisores)
- Con un flujo exportado de **tu** n8n: el ejemplo es hecho a mano con la forma del archivo exportado; la medición con 2.061 flujos reales confirma los nombres de campos, pero no tu versión.
- El revisor de bots busca patrones de texto: no sabe si la lista de usuarios se aplica de verdad ni si la comparación es correcta.
- Los 4 bots de ejemplo no se desplegaron ni se probaron contra Telegram o WhatsApp reales (necesitan tokens).

## Sobre la «activación sola»
Es si Claude abre la skill por su cuenta cuando el usuario pide algo parecido. Con 10 skills de los tres repos cargadas a la vez, en 50 frases (30 que debían activarla y 20 que no) con Haiku: **activó la correcta en 20 de 30 y nunca una equivocada (0 de 20)**. Son pocas repeticiones, con un modelo distinto al de uso diario; sirve como señal, no como medida exacta.

## Sin probar en ninguna skill
Conexión real con Gmail, Drive, Telegram, WhatsApp o n8n (necesitan claves y no se piden ni se guardan aquí).
