# Índice de skills agregadas (para saber cuándo usar cada una)

**Instalarlas:** `bash instalar.sh --lista` muestra los grupos y `bash instalar.sh n8n firebase` instala los que elijas. En sesiones en la nube se instalan solos los grupos de `grupos-activos.txt` (hoy: `n8n` y `agentes-cloudflare`). Origen y versión de cada skill: `FUENTES.md`. Revisión de seguridad: `SEGURIDAD.md`.

Todas son de terceros, con licencia libre (MIT o Apache-2.0). Cada carpeta de origen trae su licencia en `third-party/`.
No se probó ninguna en una tarea real; solo se verificó que el archivo `SKILL.md` es válido y que no tiene comandos de riesgo.

## n8n (agentes y automatizaciones)
Origen: czlonkowski/n8n-skills (MIT). Entrada: `using-n8n-mcp-skills`.

| Skill | Cuándo usarla |
|---|---|
| using-n8n-mcp-skills | Cualquier tarea de n8n; te manda a la skill correcta. |
| n8n-workflow-patterns | Diseñar un flujo nuevo (webhook, API, lotes, horarios). |
| n8n-node-configuration | Configurar los campos de un nodo. |
| n8n-expression-syntax | Escribir `{{ }}` y pasar datos entre nodos. |
| n8n-code-javascript / n8n-code-python | Nodo Code. |
| n8n-code-tool | Herramienta de código para un agente de IA. |
| n8n-agents | Agentes de IA, memoria, herramientas, RAG. |
| n8n-subworkflows | Dividir en sub-flujos reutilizables. |
| n8n-error-handling | Que los fallos no pasen en silencio. |
| n8n-validation-expert | Entender errores y avisos de validación. |
| n8n-binary-and-data | Archivos, imágenes, PDF. |
| n8n-mcp-tools-expert | Usar las herramientas de n8n-mcp. |
| **revisar-flujo-n8n** (original) | Revisar un flujo exportado: claves escritas, webhooks abiertos, bot sin filtro de usuario, sin manejo de errores. Trae revisor automático. |
| n8n-multi-instance | Más de una instancia de n8n. |
| n8n-self-hosting | Instalar n8n propio con Docker. |
| **plantillas-n8n** (original) | Partir de un flujo ya hecho: buscar en una biblioteca de unos 2.000 flujos, limpiarlo y adaptarlo. |

## Agentes en Cloudflare
- **crear-agente** (santmun, MIT): guía en español para crear un agente de IA en Cloudflare.

## Cloudflare (apps y Workers)
Origen: cloudflare/skills (Apache-2.0).

| Skill | Cuándo usarla |
|---|---|
| cloudflare | No sé qué producto de Cloudflare usar. |
| wrangler | Comandos de Wrangler, desarrollo local y despliegue. |
| workers-best-practices | Escribir o revisar un Worker. |
| web-perf | Velocidad de carga de una web. |
| durable-objects | Estado y coordinación entre usuarios. |
| agents-sdk | Agentes de IA con el SDK de Cloudflare. |

## Firebase
Origen: firebase/agent-skills (Apache-2.0).

| Skill | Cuándo usarla |
|---|---|
| firebase-basics | Instalar la herramienta de Firebase, iniciar sesión, crear o elegir proyecto. |
| firebase-auth-basics | Inicio de sesión de usuarios. |
| firebase-firestore | Base de datos Firestore. |
| firestore-rules-creation | Escribir las reglas de seguridad de Firestore. |
| firebase-security-rules-auditor | Revisar si las reglas tienen huecos. |
| firebase-hosting-basics | Publicar una web estática o SPA. |
| firebase-ai-logic-basics | Usar Gemini dentro de una app con Firebase. |

## MCP
Origen: anthropics/skills (Apache-2.0).

| Skill | Cuándo usarla |
|---|---|
| mcp-builder | Crear un servidor MCP propio. |

## Gemini (oficiales de Google)
Origen: google-gemini/gemini-skills (Apache-2.0).

| Skill | Cuándo usarla |
|---|---|
| gemini-api-dev | Programar llamadas a la API de Gemini: texto, chat, imágenes y archivos. |
| gemini-live-api-dev | Voz y video en tiempo real con Gemini Live. |

## Calidad y seguridad de agentes (originales)
| Skill | Cuándo usarla |
|---|---|
| **probar-prompts** | Probar un prompt con casos normales, ambiguos y de engaño, con promptfoo. |
| **seguridad-agentes** | Revisar la seguridad de un agente antes de conectarlo a correo, archivos o mensajes. Trae `revisar_bot.py` (lee el código) y `probar_webhook.py` (le escribe al bot corriendo con mensajes falsos). |

## APIs y mensajería (originales)
| Skill | Cuándo usarla |
|---|---|
| **apis-gratis** | Elegir un modelo, una API o un aviso al teléfono gratis, con sus límites y riesgos. |
| **bot-telegram** | Un bot de Telegram gratis en Cloudflare Workers, con lista de usuarios permitidos. |
| **whatsapp-cloud-api** | Conectar un agente a la API oficial de WhatsApp: webhook, firma, ventana de 24 horas. |

## Videos infantiles en YouTube (original)
| Skill | Cuándo usarla |
|---|---|
| **agente-youtube-infantil** | Montar en n8n un investigador de videos infantiles virales (te los manda por Telegram) y una subida a YouTube que es siempre **privada y «para niños»** hasta que pulses «Publicar». Trae el código de cada nodo, tres plantillas para importar y pruebas. Todavía no crea los videos ni mira estadísticas. |

## Se movieron a `app-skills-jeiler`
`frontend-design`, `webapp-testing`, `theme-factory` y `canvas-design`: no son de agentes y estaban repetidas.

## Skills de Vercel heredadas del fork
En `skills/` siguen las skills originales de Vercel (`react-best-practices`, `composition-patterns`, `react-view-transitions`, `react-native-skills`, `web-design-guidelines`, `deploy-to-vercel` y otras). **No las borré**, para seguir recibiendo actualizaciones del original.
Cuatro de ellas tienen el mismo nombre que copias en `app-skills-jeiler` o `apk-skills-jeiler`: **no instalar las dos copias en la misma sesión.** `instalar.sh` no las incluye en ningún grupo.

## Revisadas y NO incluidas
- gemini-api-cli (Google): su instalación ejecuta un script descargado (`curl ... | bash`). No se copió.
- clasp-skill (tnisizawa, Apps Script): está escrita en japonés y tiene muy poco uso. No se copió.
- win11-admin-skill (optimaquantum): 830 líneas, 2 estrellas, activación «proactiva» para cualquier tarea de Windows, trae una ruta personal del autor. Cambia registro y servicios; no la recomiendo sin más pruebas.
