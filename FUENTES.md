# Fuentes de las skills copiadas

Cada fila dice de dónde viene una skill, qué versión se copió y con qué licencia. Sirve para saber si hay una versión nueva en el origen (se compara el commit).
Las copias de los repos propios (forks) pueden ir atrasadas frente al original. Verificado el 2026-11-04.

| Skills | Origen | Commit copiado | Fecha | Licencia |
|---|---|---|---|---|
| 14 `n8n-*` y `using-n8n-mcp-skills` | czlonkowski/n8n-skills | e037563 | 2026-10-24 | MIT |
| `crear-agente` | santmun/crear-agente (**modificada**: la `description` pasó a bloque `>-` para que el YAML sea válido y se acortó de 1.166 a 888 caracteres (límite de 1.024); sin cambiar su sentido) | 9c5d246 | 2026-07-09 | MIT |
| `mcp-builder` | anthropics/skills | ca45fc4 | 2026-10-28 | Apache-2.0 |
| 7 de Firebase | firebase/agent-skills | b76be96 | 2026-11-03 | Apache-2.0 |
| `gemini-api-dev`, `gemini-live-api-dev` | google-gemini/gemini-skills | e1f29de | 2026-11-03 | Apache-2.0 |
| 6 de Cloudflare | cloudflare/skills | 1f2cd0a | 2026-11-03 | Apache-2.0 |
| Skills originales de Vercel (heredadas del fork) | vercel-labs/agent-skills | 063bee9 | 2026-08-28 | Cada skill declara la suya; el repo de origen no trae LICENSE |

Originales de este repo (licencia MIT, ver `LICENSE-originales`): `revisar-flujo-n8n`, `probar-prompts`, `seguridad-agentes`, `apis-gratis`, `bot-telegram`, `plantillas-n8n`, `whatsapp-cloud-api`, `agente-youtube-infantil`.

## Revisar si hay versiones nuevas (cada mes)
```bash
python -I comparar-fuentes.py
```
Es de solo lectura: compara cada commit de esta tabla con el más nuevo del repo de origen y dice «igual» o «HAY CAMBIOS» (o no pudo consultar). Salida 0 = todo igual, 1 = hay cambios, 2 = no se pudo consultar alguno. Que haya cambios no obliga a actualizar: primero mirar qué cambió, volver a revisar su seguridad (`SEGURIDAD.md`) y actualizar la fila de esta tabla. Probado el 2026-11-04.

También avisa cuando la tabla de límites de `apis-gratis` tiene 3 meses o más: ahí hay que volver a verificar los planes gratuitos en las páginas oficiales.

## Herramientas externas que se usan pero NO se copian al repo
| Herramienta | Versión | Licencia | Para qué | Cómo se verificó |
|---|---|---|---|---|
| valn8n (DrMicrobit/valn8n) | 0.1.1 | MIT | Revisar la estructura de un flujo de n8n (opcional) | Código fuente leído con búsqueda de riesgos; instalada aparte |
| wrangler / workerd (Cloudflare) | 4.158.0 / 1.20261104.1 | MIT o Apache-2.0 / Apache-2.0 | Correr un bot en local para probarlo | Licencia leída en su `package.json` |
| grammy | 1.46.0 | MIT | Librería del bot de ejemplo | Licencia en su `package.json` |
| actionlint (rhysd/actionlint) | 1.7.12 | MIT | Errores de escritura en flujos de GitHub Actions | Huella SHA-256 del binario comparada con la lista oficial |
| zizmor (zizmorcore/zizmor) | 1.32.0 | MIT | Seguridad de flujos de GitHub Actions | Licencia en PyPI; se usa con `--offline` |
| gitleaks | 8.30.0 | MIT | Claves escritas en archivos e historial | Huella SHA-256 verificada |
| REA (tu fork `rea.-`, morluto/rea) | 6.5.0 | MIT | Mirar páginas por dentro (se usó para probar los revisores de PWA, en `app-skills-jeiler`) | Construido en una copia temporal; el repo no se modificó |
| n8n 2.46.6 (n8n.io) | 2.46.6 | «Sustainable Use» (código visible; **no** es una licencia abierta de la lista) | Importar y validar las plantillas de `agente-youtube-infantil` y correr un nodo «Code» de verdad | Instalado en una carpeta temporal fuera del repo, sin cuentas ni claves; **no se copió código suyo**, solo se leyeron nombres de campos |
| Node.js 24 (paquete `node` de npm) | 24.22.2 | MIT | n8n 2.46.6 no arranca con Node 22 | Instalado aparte, solo para la prueba |
