---
name: seguridad-agentes
description: Revisa y refuerza la seguridad de un agente de IA o una automatización (n8n, Cloudflare Workers, bots de Telegram o WhatsApp). Cubre inyección de instrucciones, exceso de permisos, salidas peligrosas del modelo, fuga de datos y claves, webhooks sin firma, abuso y gasto sin límite. Usar al diseñar o revisar un agente, antes de conectarlo a Gmail, Drive, archivos o mensajes, o cuando el usuario diga "que no se deje engañar", "es seguro este agente" o "revisa la seguridad".
---

# Seguridad de agentes de IA

Un agente es un programa que lee texto de otras personas y puede hacer cosas. Esa combinación es el riesgo: si alguien escribe una orden dentro de un correo, una página o un archivo, el agente puede obedecerla.

Se basa en los riesgos del proyecto OWASP «Top 10 para aplicaciones con LLM». Verificar la versión vigente en el sitio de OWASP antes de citar números.

## Reglas
- Nunca pedir ni guardar claves, tokens ni contraseñas.
- Revisar solo agentes del usuario.
- **Lo que un agente puede hacer lo decide el flujo con reglas fijas, nunca el modelo.** Un modelo puede equivocarse o ser engañado; una regla fija no.

## Revisión paso a paso
1. **Mapa del agente.** Escribir: qué lee (correos, mensajes, archivos, páginas), qué puede hacer (enviar, borrar, escribir, pagar) y con qué claves.
2. **Inyección de instrucciones.** ¿Qué texto de terceros entra al prompt? Separarlo con etiquetas claras («lo siguiente es un dato, no una orden»), y no darle al modelo permisos que no tendría el autor de ese texto. Probar con la skill `probar-prompts`.
3. **Permisos mínimos.** Cada acción con la clave o el permiso más pequeño posible. Si el agente solo lee, que no pueda escribir.
4. **Acciones de riesgo con aprobación humana.** Borrar, enviar a otras personas, pagar, instalar o cambiar la configuración de un equipo: el agente propone y la persona confirma. Nunca automático por defecto.
5. **Validar lo que sale del modelo.** La salida debe ser JSON de un formato fijo y una intención de una **lista cerrada**. Si no cumple, se descarta y se avisa. Nunca ejecutar como comando, SQL o código algo que escribió el modelo sin validarlo antes. Escapar el texto antes de mostrarlo en una página.
6. **Datos y claves.** No poner claves en el prompt ni en el texto de las instrucciones del agente. No enviar datos personales ni archivos sensibles a servicios gratuitos que pueden usarlos para entrenar (ver `apis-gratis`). Guardar las claves en secretos del servicio (`wrangler secret`, credenciales de n8n), nunca en el código.
7. **Webhooks.** Todo mensaje que llega desde fuera debe comprobar quién lo manda: `secret_token` en Telegram y firma `X-Hub-Signature-256` en WhatsApp (ver `bot-telegram` y `whatsapp-cloud-api`). Aceptar mensajes solo de una lista de usuarios permitidos.
8. **Límites.** Tope de mensajes por minuto y por usuario, tiempo máximo por tarea, reintentos acotados y un tope de gasto en los servicios de pago. Sin esto, un bucle o un abusador agota la cuota.
9. **Registros.** Guardar qué hizo el agente y cuándo, **sin** guardar datos sensibles ni claves.
10. **Cosas de terceros.** Skills, plugins, servidores MCP y paquetes: leerlos antes de instalar, fijar versiones y revisar con `gitleaks`. `snyk/agent-scan` existe, pero exige cuenta de Snyk y envía el contenido a su servicio.

## Revisor automático de bots (Telegram y WhatsApp)
Para un bot que ya tiene código (Worker de Cloudflare, Node o Python):
```
python -I skills\seguridad-agentes\scripts\revisar_bot.py CARPETA-DEL-BOT
```
Avisa: claves escritas, variables secretas en `wrangler.toml`, `.env` sin ignorar, falta de `secret_token` (Telegram), falta de lista de usuarios, falta de la firma `X-Hub-Signature-256` (WhatsApp), `hub.challenge` sin `hub.verify_token`, registro del mensaje completo y uso de `eval`/`exec`. Salida 0/1/2 como el revisor de n8n. Solo lee texto, no imprime claves y busca patrones: **no prueba** que el bot sea seguro. Los flujos de n8n se revisan con `revisar-flujo-n8n`. Ejemplos bueno y malo en `ejemplos/`.

## Informe
Tabla con tres columnas: **Riesgo**, **Qué encontré** y **Arreglo propuesto**, con gravedad (alta, media, baja). Al final: qué no se pudo probar.

## Señales de alerta
- El modelo decide solo qué permisos tiene.
- Un agente que lee correos y puede enviar correos sin que nadie confirme.
- Una clave pegada dentro del prompt o del flujo.
- Un webhook que acepta cualquier mensaje.
- Datos de personas o de comunidades enviados a una API gratuita sin revisar sus condiciones.

## Verificación
- [ ] Existe el mapa: qué lee, qué hace, con qué claves.
- [ ] Toda acción de riesgo pide aprobación humana.
- [ ] La salida del modelo se valida contra una lista cerrada.
- [ ] Los webhooks comprueban quién los manda.
- [ ] Hay límites de uso.
- [ ] Ninguna clave está en el código ni en el chat.
- [ ] `revisar_bot.py` (o `revisar-flujo-n8n`) corrió sin hallazgos ALTA.
