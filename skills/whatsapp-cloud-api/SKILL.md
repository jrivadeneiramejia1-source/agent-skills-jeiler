---
name: whatsapp-cloud-api
description: Guía para conectar un agente o un flujo de n8n a la API oficial de WhatsApp Business (Cloud API) de Meta. Cubre la verificación del webhook, la firma de cada mensaje, la ventana de 24 horas, las plantillas aprobadas, el costo por mensaje y los riesgos de las librerías no oficiales. Usar cuando el usuario diga "auto-respuesta de WhatsApp", "un agente en WhatsApp", "webhook de WhatsApp" o "enviar mensajes por WhatsApp".
---

# WhatsApp Business (Cloud API)

## Reglas
- **Nunca pedir ni guardar** el token de acceso ni el «App Secret». El usuario los guarda como secretos.
- **Los precios y las reglas cambian.** Lo escrito abajo es de las búsquedas del 2026-11-04 (la regla de octubre de 2026 viene de la página oficial de Meta; otros datos, de blogs de proveedores). **Verificar en la página oficial de precios de Meta antes de decidir.**
- No usar librerías no oficiales con el número principal del usuario.

## Cómo funciona
1. **Verificación del webhook (una vez).** Meta hace una petición GET a tu dirección con `hub.mode`, `hub.verify_token` y `hub.challenge`. Si `hub.verify_token` coincide con la palabra que tú configuraste, respondes con código 200 y devuelves el valor de `hub.challenge`.
2. **Firma de cada mensaje.** Cada mensaje llega por POST con el encabezado `X-Hub-Signature-256`. Se calcula un HMAC-SHA256 del **cuerpo exacto sin modificar** con el «App Secret» y se compara con el valor que viene después de `sha256=`. Volver a escribir el JSON antes de calcularlo cambia los bytes y rompe la comprobación. Si no coincide, se descarta el mensaje.
3. **Ventana de 24 horas.** Cuando un cliente te escribe, se abre una ventana de 24 horas; cada mensaje nuevo del cliente la reinicia. Dentro de la ventana puedes responder con texto libre. **Fuera de la ventana solo se pueden enviar plantillas aprobadas por Meta.**
4. **Plantillas.** Mensajes con formato fijo que Meta debe aprobar antes de usarlos. Para avisos iniciados por el negocio.
5. **Costo.** Desde el 1 de julio de 2025 Meta cobra **por mensaje de plantilla entregado**, no por conversación de 24 horas. El precio depende de la categoría (marketing, utilidad, autenticación) y del país. **Desde el 1 de octubre de 2026 también se cobran los mensajes dentro de la ventana de 24 horas** (los de «servicio», o sea las respuestas de texto libre): la página oficial de precios de Meta, actualizada el 2026-09-30, dice que se cobra cada mensaje entregado. Cada número de teléfono tiene **1.000 mensajes de servicio gratis al mes** (no se acumulan) y desde el 1.001 se cobra, con la misma tarifa que utilidad y autenticación. Sin método de pago registrado, Meta no entrega los mensajes pasada la cuota gratis. Esto se leyó en el resumen de una búsqueda, no en la página completa: confirmar la tarifa de tu país en la página oficial antes de montar algo.

## En n8n
n8n tiene nodos para WhatsApp Business Cloud (un disparador y un nodo de envío). Confirmar los nombres y la versión en tu n8n. Si el flujo recibe mensajes por webhook propio, aplicar la comprobación de la firma del punto 2.

## Pasos para un agente de respuesta automática
1. Crear la cuenta de Meta para desarrolladores y la aplicación de WhatsApp Business (lo hace el usuario; el proceso de Meta puede pedir verificar el negocio).
2. Guardar como secretos: token de acceso, App Secret y la palabra de verificación.
3. Montar el webhook con verificación (punto 1) y firma (punto 2).
4. Responder solo dentro de la ventana; para lo demás, plantillas.
5. Limitar usuarios y mensajes por minuto, y pedir confirmación en acciones de riesgo. Ver `seguridad-agentes`.
6. Probar con un número de prueba y datos inventados.

## Librerías no oficiales
Las que se conectan como «WhatsApp Web» (por ejemplo Baileys o whatsapp-web.js) **pueden provocar el bloqueo del número** y no cuentan con garantías de Meta. Si se usan, que sea con un número de pruebas, nunca con el principal.

## Fuentes consultadas (2026-11-04)
- Documentación oficial de Meta: «Create a webhook endpoint» (WhatsApp Business Platform), en developers.facebook.com.
- Guías de terceros sobre webhooks de WhatsApp (hookdeck.com) y sobre precios (courier.com, omnichat.ai). Son blogs, no documentos oficiales.

## Revisar el bot
`python -I skills\seguridad-agentes\scripts\revisar_bot.py CARPETA-DEL-BOT` avisa si falta la firma `X-Hub-Signature-256`, la comparación de tiempo constante o el `hub.verify_token`. En `skills/seguridad-agentes/ejemplos/bot-whatsapp-bueno/` hay una verificación de firma con HMAC probada con 8 casos (firma buena, cuerpo alterado, secreto distinto, encabezado ausente o mal formado).

## Qué no se probó
Nada de esto se probó con una cuenta real de WhatsApp: la skill resume la documentación y no se ejecutó contra la API.

## Verificación
- [ ] El webhook verifica el token y la firma.
- [ ] Fuera de la ventana de 24 horas solo se envían plantillas.
- [ ] Se verificó el precio vigente en la página oficial de Meta.
- [ ] Ningún secreto está en el código ni en el chat.
