---
name: revisar-flujo-n8n
description: Revisa un flujo de n8n exportado (archivo .json) y avisa riesgos antes de usarlo o subirlo a GitHub. Busca claves escritas en los nodos, webhooks sin autenticación, bots de Telegram abiertos a cualquiera, comandos del sistema, agentes con herramientas peligrosas, flujos sin manejo de errores, datos de prueba guardados y correos o teléfonos reales. Usar cuando el usuario diga "revisa este flujo", "es seguro este flujo de n8n", "voy a subir el flujo a GitHub", "importé una plantilla de n8n" o antes de activar un flujo nuevo.
---

# Revisar un flujo de n8n

Un flujo de n8n exportado es un archivo `.json`. Ahí pueden quedar claves, datos de prueba y webhooks abiertos. Esta skill trae un **revisor automático** que lo lee y avisa, y una lista de reglas con su fuente.

## Reglas
- Solo revisar flujos del usuario. Nunca pedirle ni guardar claves: el revisor **no imprime valores**, solo dice en qué nodo encontró algo.
- Un flujo que sale «limpio» **no es necesariamente seguro**: el revisor busca patrones conocidos. Lo que el flujo hace con los datos sigue necesitando criterio (ver `seguridad-agentes`).
- Si el flujo vino de una plantilla de terceros, revisarlo **antes** de importarlo y no activarlo hasta entenderlo (ver `plantillas-n8n`).

## Pasos
1. En n8n: menú del flujo → **Download** (descargar). Guardar el `.json` fuera de cualquier repo público.
2. Correr el revisor (solo Python, sin instalar nada):
   ```
   python -I skills\revisar-flujo-n8n\scripts\revisar_flujo.py MI-FLUJO.json
   ```
   Salida 0 = sin hallazgos graves; 1 = hay ALTA; 2 = el archivo no se pudo leer. Con `--json` da el resultado en JSON.
3. Arreglar primero las **ALTA**, luego las MEDIA. Cada hallazgo trae el id (F01…F14); la explicación y la fuente de cada regla está en `references/reglas.md`.
4. Si encontró una clave real: **cambiarla en el servicio** (la que estuvo escrita ya no es secreta), usar una credencial de n8n y volver a exportar.
5. Antes de subir a GitHub: sin `pinData`, sin credenciales, sin correos ni teléfonos reales, flujo desactivado.

## Qué revisa
| Id | Gravedad | Qué avisa |
|---|---|---|
| F01 F02 | ALTA | Clave o token escrito en un nodo, o encabezado `Authorization`/`api-key` con valor fijo. |
| F03 | ALTA o MEDIA | Webhook sin autenticación (ALTA si el flujo además envía, escribe o ejecuta). |
| F04 | ALTA | Disparador de Telegram sin ningún filtro del número de usuario. |
| F05 | ALTA o MEDIA | Nodo que ejecuta comandos, o código con `eval`/`child_process`. |
| F06 | MEDIA | Agente de IA con herramientas que pueden enviar, escribir o ejecutar. |
| F07 | MEDIA | Sin «Error workflow» ni «On Error»: los fallos pasan en silencio. |
| F08 | MEDIA | `pinData`: datos de prueba guardados dentro del flujo. |
| F09 | MEDIA | Certificados no válidos aceptados o llamadas `http://`. |
| F10 | MEDIA | Correo o teléfono escrito en un nodo. |
| F11 | BAJA | Exportado como activo, o nodos apagados. |
| F12 | ALTA o MEDIA | Subida a YouTube sin `privacyStatus` fijo en `private` (ALTA si falta o es `public`). |
| F13 | MEDIA | Subida o paso a público sin declarar `selfDeclaredMadeForKids`. |
| F14 | ALTA | Poner un video en `public` sin una aprobación (`sendAndWait` + IF) en el camino. Ver `agente-youtube-infantil`. |

## Herramienta complementaria (opcional): valn8n
`revisar_flujo.py` se enfoca en **seguridad**. Para **estructura** (nodos sueltos, parámetros que no existen para esa versión del nodo, expresiones mal escritas, falta de `onError`) existe `valn8n` (MIT, Python 3.13 y `uv`): `valn8n check MI-FLUJO.json`. Es un proyecto joven (versión 0.1.1, pocas estrellas): úsalo como segunda opinión, no como única revisión. Detalle, revisión de seguridad y medición en `references/herramientas.md`.

## Probado
Ver `ejemplos/`: `flujo-bueno.json` (0 hallazgos) y `flujo-malo.json` (hecho a propósito, 14 hallazgos, 5 graves, salida 1). El token del ejemplo malo es inventado. Detalle en `PRUEBAS.md` del repo.

## Señales de alerta
- Un flujo descargado de internet que ya viene **activo**.
- Un disparador de Telegram o WhatsApp sin IF que compare el usuario.
- Un agente que lee mensajes de otras personas y puede enviar correos sin confirmación.

## Verificación
- [ ] El revisor sale con 0 (o cada ALTA quedó arreglada o justificada por escrito).
- [ ] Ninguna clave dentro del `.json`; todas en credenciales de n8n.
- [ ] El flujo tiene «Error workflow».
- [ ] Sin `pinData` si el archivo se va a compartir.
