# Herramientas para revisar flujos de n8n

Marcas: **[F]** fuente abierta citada · **[P]** regla práctica sin verificar · **[E]** hecha y medida aquí. Consultado el 2026-11-06.

## valn8n (opcional, solo estructura)
| Dato | Valor |
|---|---|
| Origen | github.com/DrMicrobit/valn8n (PyPI: `valn8n`) |
| Licencia | MIT **[F]** (pyproject.toml y README) |
| Versión probada | 0.1.1 (3 commits, 2 estrellas: proyecto joven) |
| Requisitos | Python 3.13 o más; dependencias `json-source-map` y `rich` |
| Uso | `valn8n check flujo.json` (o una carpeta); `--strict-only` para solo reglas estrictas; salida 0/1/2 |
| Qué revisa | Sintaxis y semántica del JSON: parámetros de nodos según su versión, expresiones, conexiones, credenciales, manejo de errores, nombres y notas (reglas ND01–ND08) |

**Revisión de seguridad antes de usarlo [E]:** se bajó el código fuente (5.698 líneas de Python) y se buscó `socket`, `subprocess`, `requests`, `urllib`, `os.system`, `eval`, `exec`, `urlopen` y `__import__`: **cero coincidencias**; solo lee los archivos que se le dan. Se instaló en un entorno aparte, sin claves. No se copió nada a este repo.

**Medido [E]** sobre mis ejemplos:
- `flujo-bueno.json`: 12 avisos en la primera pasada (0 errores). Uno era un **fallo real de mi ejemplo**: el nodo IF mezclaba el formato nuevo de condiciones con `typeVersion` 1 (`ND0301`); se corrigió con `typeVersion` 2.2 y desapareció. Los demás son consejos (notas, `onError` en nodos externos, credenciales presentes en el archivo exportado, que n8n siempre incluye).
- `flujo-malo.json`: 13 avisos (0 errores) sobre estructura y manejo de errores, **pero no detecta** lo grave: ni el webhook abierto, ni `executeCommand`, ni el bot de Telegram sin filtro, ni el token escrito. Por eso **no reemplaza** a `revisar_flujo.py`; se complementan.
- Falsos avisos vistos: marca «sin conexión entrante» a un nodo Webhook (que es un disparador). Tomar sus avisos como consejos, no como veredicto.

## cekuu35/n8n-workflow-audit (no usada)
Busca claves escritas y webhooks abiertos (MIT, 4 commits, 0 estrellas). Cubre lo mismo que `revisar_flujo.py`, con menos señales de uso: **no se instaló**.

## Guía oficial de seguridad de n8n [F]
docs.n8n.io/hosting/securing/overview/ (para instalaciones propias): auditoría de seguridad, políticas (MFA), SSL forzado, SSO, rotación de la clave que cifra credenciales, redacción de datos de ejecución, API pública desactivada, telemetría desactivada, bloqueo de nodos específicos, protección SSRF, verificación de correo y *task runners* reforzados para el nodo Code. La página **no** da nombres de variables de entorno, así que no se citan aquí (ver la skill `n8n-self-hosting`).

## Licencia de n8n
n8n usa la «Sustainable Use License» (código disponible, no es una licencia abierta como MIT). Esta skill no copia código de n8n; solo lee flujos exportados por el usuario **[P]** (verificar la licencia vigente en el repositorio de n8n antes de redistribuir algo suyo).
