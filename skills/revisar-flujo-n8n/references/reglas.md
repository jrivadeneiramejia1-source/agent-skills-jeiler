# Reglas del revisor de flujos de n8n

Marcas: **[F]** fuente abierta citada · **[P]** regla práctica sin verificar en una fuente · **[E]** hecha y medida aquí.
Fuentes consultadas el 2026-11-06 (ver `fuentes.md`). No se copió texto de ellas, solo frases cortas citadas.

| Id | Regla | Marca | Base |
|---|---|---|---|
| F01 | Una clave escrita en un nodo queda en el archivo exportado y en el historial de git. Las claves van en credenciales de n8n. | [P] | Regla general de seguridad; `gitleaks` busca lo mismo. |
| F01 | El patrón del token de Telegram debe aceptar `/bot123456789:TOKEN` (sin límite de palabra antes del número). | [E] | Un ejemplo malo hecho a propósito lo dejó pasar al principio; corregido (ver `LECCIONES.md`). |
| F02 | Encabezados como `Authorization` o `x-api-key` con valor fijo en un nodo HTTP: usar autenticación por credencial. | [P] | Misma razón que F01. |
| F03 | El nodo Webhook ofrece autenticación Basic, Header y JWT; «None» lo deja abierto. Existe además «IP(s) Allowlist». | [F] | docs.n8n.io, nodo Webhook: «The node supports Basic auth, Header auth and JWT auth… None». |
| F04 | Un bot de Telegram debe comparar `message.from.id` con una lista de usuarios permitidos. | [P] | Es lo que hace `bot-telegram` (Cloudflare); en n8n se hace con un nodo IF. |
| F05 | Comandos del sistema y `eval` con texto que escribió una persona = ejecución remota de código. | [P] | Regla general; ver `seguridad-agentes` paso 5. |
| F06 | Acciones de riesgo con aprobación humana. | [P] | `seguridad-agentes` paso 4. |
| F07 | Un «Error workflow» corre cuando falla otro flujo; debe empezar con un nodo Error Trigger. Se elige en Options → Settings. | [F] | docs.n8n.io, «Error handling». |
| F08 | `pinData` guarda datos de prueba dentro del flujo. | [E] | Medido el 2026-11-04 en la biblioteca de plantillas: 136 de 2.061 flujos lo traían (ver `PRUEBAS.md`). |
| F09 | No aceptar certificados inválidos; no usar `http://` fuera de la máquina local. | [P] | Regla general. |
| F10 | Correos y teléfonos reales no van en un repo público. | [E] | La misma medición: 286 de 2.061 flujos traían correos escritos. |
| F11 | Un flujo exportado `active: true` se enciende al importarlo. | [E] | Medición: 217 de 2.061 plantillas estaban activas. |

## Límites del revisor
- Busca patrones de texto. No sabe si un nodo IF realmente bloquea a los demás: solo ve que existe uno que menciona `from.id`.
- No ve credenciales guardadas dentro de n8n, solo lo que hay en el archivo.
- No revisa expresiones complejas ni sub-flujos que viven en otros archivos.
