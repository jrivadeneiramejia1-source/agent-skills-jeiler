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
  - `skills/workers-best-practices/references/configuration.md`: ejemplo de lo que NO se debe hacer (`"API_KEY": "sk-live-abc123..."`, con la nota «Secret in version control»).
- **Comandos de riesgo:** ninguno en las skills de n8n, Firebase, Cloudflare ni `mcp-builder`.
- **`crear-agente` merece cuidado:** sus instrucciones le piden al estudiante ejecutar `curl ... | bash` (el instalador de la propia skill, y el instalador de Node de NodeSource con `sudo`). Es la forma habitual de instalar esas herramientas, pero ejecuta código descargado. Revisar esas instrucciones antes de seguirlas.
- **No revisé** las skills originales de Vercel que vienen en el fork.
