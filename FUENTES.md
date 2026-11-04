# Fuentes de las skills copiadas

Cada fila dice de dónde viene una skill, qué versión se copió y con qué licencia. Sirve para saber si hay una versión nueva en el origen (se compara el commit).
Las copias de los repos propios (forks) pueden ir atrasadas frente al original. Verificado el 2026-11-04.

| Skills | Origen | Commit copiado | Fecha | Licencia |
|---|---|---|---|---|
| 14 `n8n-*` y `using-n8n-mcp-skills` | czlonkowski/n8n-skills | e037563 | 2026-10-24 | MIT |
| `crear-agente` | santmun/crear-agente | 9c5d246 | 2026-07-09 | MIT |
| `mcp-builder` | anthropics/skills | ca45fc4 | 2026-10-28 | Apache-2.0 |
| 7 de Firebase | firebase/agent-skills | b76be96 | 2026-11-03 | Apache-2.0 |
| `gemini-api-dev`, `gemini-live-api-dev` | google-gemini/gemini-skills | e1f29de | 2026-11-03 | Apache-2.0 |
| 6 de Cloudflare | cloudflare/skills | 1f2cd0a | 2026-11-03 | Apache-2.0 |
| Skills originales de Vercel (heredadas del fork) | vercel-labs/agent-skills | 063bee9 | 2026-08-28 | Cada skill declara la suya; el repo de origen no trae LICENSE |

Originales de este repo (licencia MIT, ver `LICENSE-originales`): `probar-prompts`, `seguridad-agentes`, `apis-gratis`, `bot-telegram`, `plantillas-n8n`, `whatsapp-cloud-api`.

## Revisar si hay versiones nuevas (cada mes)
```bash
python3 -I comparar-fuentes.py
```
Es de solo lectura: compara cada commit de esta tabla con el más nuevo del repo de origen y dice «igual» o «HAY CAMBIOS» (o no pudo consultar). Salida 0 = todo igual, 1 = hay cambios, 2 = no se pudo consultar alguno. Que haya cambios no obliga a actualizar: primero mirar qué cambió, volver a revisar su seguridad (`SEGURIDAD.md`) y actualizar la fila de esta tabla. Probado el 2026-11-04.

También avisa cuando la tabla de límites de `apis-gratis` tiene 3 meses o más: ahí hay que volver a verificar los planes gratuitos en las páginas oficiales.
