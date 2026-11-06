# Revisión de seguridad

Hecha el 2026-11-04.

## Qué se revisó y cómo
1. **gitleaks 8.30.0** (busca claves y tokens escritos en archivos). Se descargó del sitio oficial y se verificó su checksum (`OK`). Se corrió sobre los archivos actuales y sobre todo el historial de git.
2. **Búsqueda propia de comandos de riesgo** en los scripts de las skills copiadas: descargar y ejecutar a la vez (`curl ... | sh`), `eval`, `rm -rf /`, `base64 -d`, `nc -e`, `sudo`.
3. **No se ejecutó `snyk/agent-scan`.** Pide crear una cuenta en Snyk y un token, y envía el contenido de las skills a su servicio. No lo usé por eso. Queda pendiente si decides crear la cuenta tú.

## Resultado
- **gitleaks:** 5 hallazgos en los archivos actuales y en el historial. Revisé cada uno y **todos son ejemplos ficticios**, no claves reales:
  - `packages/vercel-optimize-tests/test/vercel-redaction.test.mjs`: una prueba de redacción con un token inventado (`vercel_secret_1234...`).
  - `skills/firebase-ai-logic-basics/SKILL.md`: ejemplo de formato de un token de depuración (`123a4567-...`).
  - `skills/n8n-binary-and-data/AGENT_TOOL_BINARY.md` (2 líneas): nombres de archivo de ejemplo (`sess12-abc123.png`).
  - `skills/workers-best-practices/references/configuration.md`: ejemplo de lo que NO se debe hacer: una línea `API_KEY` con un valor inventado que empieza por `sk-live`, con la nota «Secret in version control».
- **Comandos de riesgo:** ninguno en las skills de n8n, Firebase, Cloudflare ni `mcp-builder`.
- **`crear-agente` merece cuidado:** sus instrucciones le piden al estudiante ejecutar `curl ... | bash` (el instalador de la propia skill, y el instalador de Node de NodeSource con `sudo`). Es la forma habitual de instalar esas herramientas, pero ejecuta código descargado. Revisar esas instrucciones antes de seguirlas.
- **No revisé** las skills originales de Vercel que vienen en el fork.

## Fase 2 (skills nuevas, 2026-11-04)
- Se agregaron 8 skills: 2 oficiales de Google (`gemini-api-dev`, `gemini-live-api-dev`) y 6 originales. gitleaks no encontró nada nuevo, y la búsqueda de comandos de riesgo salió vacía.
- Se dejó fuera `gemini-api-cli`: su instalación ejecuta un script descargado (`curl ... | bash`).
- `plantillas-n8n` apunta a una biblioteca de flujos de terceros (no se copió al repo). Trae un script que quita credenciales y datos de prueba antes de importar.
- Las skills originales no se han probado en tareas reales. Lo probado de forma parcial está dicho en cada una (`probar-prompts` con promptfoo sin internet; `bot-telegram` con llamadas simuladas; `plantillas-n8n` con el script de limpieza).

## Fase 3 (2026-11-06)
- Se agregó 1 skill original (`revisar-flujo-n8n`) y scripts originales (`revisar_flujo.py`, `revisar_bot.py`). Son solo Python estándar: no abren redes, no ejecutan lo que revisan y no imprimen valores de claves. Sin código de terceros nuevo.
- **gitleaks 8.30.0** se volvió a descargar del sitio oficial (checksum `OK`) y se corrió sobre los archivos: **los mismos 5 hallazgos** de antes (todos ejemplos ficticios). Lo nuevo no agregó ninguno.
- Los ejemplos malos traen un token inventado (`000000000:FAKEFAKE…`) a propósito para probar los revisores; no es una clave real.
- Se borraron 5 `.zip` repetidos de `skills/` (copias empaquetadas de carpetas que ya estaban). El historial de git los conserva.
- `crear-agente` (de terceros): la línea `description` no era YAML válido (tenía «Stack base: …» sin comillas), así que un lector estricto podía no cargarla. Se envolvió en un bloque `>-` sin cambiar el texto. Anotado en `FUENTES.md`.

## Fase 4 (2026-11-06, segunda ronda)
- Herramientas de terceros que se **usaron** (no se copiaron al repo): `valn8n` 0.1.1 (MIT) tras leer su código (0 coincidencias de red/ejecución) en un entorno aparte; `wrangler` 4.158.0 (MIT o Apache-2.0), `workerd` 1.20261104.1 (Apache-2.0) y `grammy` 1.46.0 (MIT) solo para correr bots de ejemplo en local con claves inventadas; `actionlint` 1.7.12 (MIT, binario con huella SHA-256 verificada contra la lista oficial) y `zizmor` 1.32.0 (MIT, `--offline`). Detalle en `FUENTES.md`.
- **gitleaks sobre el historial completo** (287 commits): 6 hallazgos, todos ejemplos ficticios (ver `PRUEBAS.md`).
- `probar_webhook.py` solo habla con direcciones locales salvo `--permitir-remoto` (para bots del propio usuario) y no guarda ni imprime las claves que recibe.
- Nuevo `.github/workflows/pruebas.yml`: corre las pruebas sin secretos, con permisos de solo lectura, `actions/checkout` fijado a commit y `persist-credentials: false`.
