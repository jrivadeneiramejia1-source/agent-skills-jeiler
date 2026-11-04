---
name: apis-gratis
description: Ayuda a elegir APIs y servicios gratuitos para un agente o una app (modelos de lenguaje, clima, mapas, monedas, avisos al teléfono), con sus límites, si piden clave y qué riesgos tienen para los datos. Usar cuando el usuario diga "qué API gratis uso", "necesito un modelo gratis", "cómo mando avisos al teléfono sin pagar", "un servicio gratuito para esto" o cuando un agente necesite un servicio externo.
---

# APIs y servicios gratuitos

Los planes gratuitos cambian seguido. Los números de este archivo son una **foto del 2026-10** tomada de las listas del propio usuario. **Antes de decidir, verificar el límite en la página oficial del proveedor y anotar la fecha.**

## Reglas
- **Nunca pedir ni guardar claves.** El usuario crea la cuenta y guarda la clave como secreto (`wrangler secret put`, credenciales de n8n).
- **Datos sensibles: no.** Algunos planes gratuitos pueden usar lo que se envía para mejorar o entrenar sus modelos. No mandar datos personales, archivos de comunidades ni nada irreemplazable a esos planes. Para eso, usar un modelo local o un plan que lo prohíba por escrito.
- Siempre manejar el límite: esperar y reintentar si responde «demasiadas solicitudes» (429), guardar respuestas repetidas (caché) y tener un plan B.
- Decir qué no se pudo verificar.

## Modelos de lenguaje con plan gratuito
Fuente: `awesome-free-llm-apis` (tu fork, commit `cf97c32`, 2026-10-11). Ahí están los modelos y los límites completos.

| Proveedor | Lo que dice la lista | Cuidado |
|---|---|---|
| **Google Gemini** (AI Studio) | Plan gratuito sin tarjeta. Modelos Flash: 15 solicitudes por minuto y 1.500 por día; Flash-Lite: 30 por minuto; Pro: 5 por minuto y 50 por día. | **Los mensajes del plan gratuito pueden ser usados por Google para mejorar sus productos.** |
| **Groq** | Plan gratuito sin tarjeta. Modelos `gpt-oss`: 30 por minuto y 1.000 por día. | Revisar sus condiciones de datos. |
| **Cloudflare Workers AI** | 10.000 «Neurons» por día gratis, más de 60 modelos. Se usa dentro de un Worker. | Los Neurons se gastan según el modelo; medir. |
| **Mistral** | Modo gratuito activado por defecto, cerca de 1 solicitud por segundo. | **Los mensajes del modo gratuito pueden usarse para entrenar, salvo que se desactive.** |
| **OpenRouter** | Modelos con sufijo `:free`: 20 por minuto y 50 por día. | Límite diario bajo. |

Todos usan el formato de OpenAI, así que cambiar de proveedor es cambiar la dirección y la clave.

**Un solo punto para muchos proveedores:** `freellmapi1` (tu fork, MIT) reúne decenas de proveedores gratuitos detrás de una sola dirección y cambia de uno a otro si se acaba el límite. Guarda las claves de todos (cifradas). **No usarlo sin revisarlo y sin instalarlo en un servidor propio.**

## Otras APIs sin clave
Fuente: `public-apis` (tu fork, commit `8939d46`, 2026-09-29), columna «Auth: No».

| Para qué | Servicio | Nota |
|---|---|---|
| Clima | **Open-Meteo** | Gratis para uso no comercial. |
| Mapas y direcciones | **Nominatim** (OpenStreetMap) | Tiene una política de uso estricta (pocas solicitudes por segundo, identificarse). Leerla antes. |
| Cambio de monedas | **Frankfurter** | Tasas y conversión. |
| Libros | **Open Library** | Datos y portadas. |

La lista tiene más de 50 categorías. Buscar ahí antes de crear algo desde cero.

## Avisos al teléfono sin pagar
| Opción | Cómo | Cuidado |
|---|---|---|
| **ntfy** | Un mensaje HTTP a una dirección con un nombre de tema; la app de ntfy en el teléfono lo recibe. El servidor público gratuito no pide cuenta. | En el servidor público **el nombre del tema funciona como contraseña**: cualquiera que lo sepa puede leer. Usar un nombre largo e imposible de adivinar, o instalar ntfy en un servidor propio. Verificar licencia y límites en ntfy.sh. |
| **Bot de Telegram** | Un mensaje del bot a tu chat (skill `bot-telegram`). | Solo tú debes estar en la lista de usuarios permitidos. |
| **Pushover** | Lo que usa `crear-agente`. | Es de pago. Preferir las dos anteriores. |

## Proceso para elegir
1. ¿Qué datos viajan? Si son sensibles, no hay plan gratuito válido: modelo local o plan con garantía escrita.
2. ¿Cuántas solicitudes por día necesita de verdad? Comparar con el límite.
3. Elegir 1 principal y 1 de respaldo.
4. Verificar límites y condiciones en las páginas oficiales hoy.
5. Anotar en el proyecto: proveedor, límite, fecha de verificación y qué pasa si se acaba.

## Verificación
- [ ] Se verificó el límite en la página oficial y se anotó la fecha.
- [ ] No viajan datos sensibles a un plan que pueda entrenar con ellos.
- [ ] Hay un plan B si se acaba el límite.
- [ ] Ninguna clave está en el código ni en el chat.
