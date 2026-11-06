# agent-skills-jeiler

Skills para **agentes de IA y automatizaciones**: n8n, bots de Telegram y WhatsApp, Cloudflare Workers, Firebase, Gemini y MCP.
Hermanos de este repo: `app-skills-jeiler` (apps web), `apk-skills-jeiler` (apps Android) y `servicios-skills-jeiler` (ofrecer y entregar servicios).

Cada carpeta de `skills/` es una skill: un `SKILL.md` con instrucciones para que Claude sepa cuándo y cómo usarla.

## Qué hay (grupos)
| Grupo | Para qué |
|---|---|
| `n8n` | Diseñar, configurar, depurar y revisar flujos de n8n. |
| `agentes-cloudflare` / `cloudflare` | Agentes y Workers en Cloudflare (plan gratis). |
| `firebase` / `gemini` / `mcp` | Firebase, la API de Gemini y servidores MCP. |
| `agentes-calidad` | Probar prompts, revisar la seguridad de un agente y **revisores automáticos** de flujos de n8n y de bots. |
| `apis-y-mensajeria` | APIs gratis, bot de Telegram, WhatsApp oficial. |
| `youtube` | Agente de n8n para un canal de videos infantiles: investigador de virales y subida con aprobación (privado primero). |

La lista completa, con cuándo usar cada una, está en **`INDICE-DE-SKILLS.md`**. De dónde viene cada una: `FUENTES.md`. Seguridad: `SEGURIDAD.md`. Qué se probó de verdad: `PRUEBAS.md`. Errores aprendidos: `LECCIONES.md`.

## Revisores automáticos (originales, solo Python estándar)
Revisan un archivo y avisan errores. Corren igual en Windows y en la nube; no abren redes, no ejecutan nada del archivo revisado y no muestran valores secretos.
```
python -I skills\revisar-flujo-n8n\scripts\revisar_flujo.py MI-FLUJO.json
python -I skills\seguridad-agentes\scripts\revisar_bot.py CARPETA-DEL-BOT
python -I skills\seguridad-agentes\scripts\probar_webhook.py telegram http://127.0.0.1:8787/ --secreto CLAVE-DE-PRUEBA --permitido 111111111
```
El segundo **le escribe a un bot que está corriendo** en tu computador (`wrangler dev`, con claves de prueba inventadas) y comprueba que rechaza lo que debe y que no devuelve error 5xx.
Salida 0 = sin problemas graves, 1 = hay hallazgos graves. Aviso: buscan patrones; que salgan limpios **no** prueba que el agente sea seguro.

## Instalar
```
bash instalar.sh --lista
bash instalar.sh n8n agentes-calidad
```
(En Windows, usa Git Bash o WSL para `instalar.sh`.) En sesiones en la nube se instalan solos los grupos de `grupos-activos.txt`. El instalador no pisa una skill que ya exista con el mismo nombre y que no haya instalado él. Mejor pocos grupos a la vez: cada skill gasta algo de contexto.

## Probar este repo
```
python -I -m unittest discover -s tests
```

## Skills heredadas de Vercel
Este repo nació como fork de `vercel-labs/agent-skills` (MIT). Esas skills siguen en `skills/` y no están en ningún grupo. Su README original está en `docs/vercel-README-original.md`.

## Qué falta o no está probado
Ver `PRUEBAS.md`: nada se conectó a servicios reales (Telegram, WhatsApp, n8n, Gmail) porque eso necesita claves, que no se piden ni se guardan.
