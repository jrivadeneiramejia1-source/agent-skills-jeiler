---
name: bot-telegram
description: Crea un bot de Telegram gratis que corre en Cloudflare Workers con el framework grammY, con lista de usuarios permitidos, clave secreta del webhook y token guardado como secreto. Sirve para recibir órdenes o enviar avisos al teléfono. Usar cuando el usuario diga "un bot de Telegram", "avisos por Telegram", "controlar mi agente desde Telegram" o "webhook de Telegram". No sirve para el agente de Telegram dentro de n8n, que ya funciona con sus propios nodos.
---

# Bot de Telegram en Cloudflare Workers (grammY)

## Reglas
- **El token del bot nunca se escribe en el chat ni en el código.** El usuario lo pide a @BotFather en Telegram y lo guarda él mismo como secreto (`wrangler secret put BOT_TOKEN`).
- **Solo responde a una lista de usuarios permitidos** (por su número de usuario de Telegram). A los demás los ignora.
- **El webhook se protege con una clave secreta** (`secret_token`) para que solo Telegram pueda llamarlo.
- Las acciones de riesgo (borrar, enviar a otras personas, cambiar un equipo) piden confirmación en el chat. Ver `seguridad-agentes`.

## Pasos
1. **Crear el bot.** El usuario abre Telegram, habla con @BotFather, crea el bot y guarda el token. Para saber su número de usuario, le escribe a su propio bot y se mira el campo `from.id` del mensaje que llega (por ejemplo, con un flujo de prueba que lo muestre).
2. **Crear el proyecto Worker** con Wrangler (ver las skills `wrangler` y `workers-best-practices`) y agregar la librería: `npm install grammy`.
3. **Guardar los secretos** en Cloudflare: `BOT_TOKEN`, `WEBHOOK_SECRET` (un texto largo y al azar que se inventa el usuario) y `BOT_INFO`. El valor de `BOT_INFO` es el resultado de `getMe` del bot (la propia documentación de grammY lo explica); con él el Worker no tiene que preguntarle a Telegram quién es en cada mensaje. `USUARIOS_PERMITIDOS` (números separados por coma) puede ir como variable normal.
4. **Escribir el Worker** con el esqueleto de abajo.
5. **Publicar** (`wrangler deploy`) y **registrar el webhook** en Telegram con el método `setWebhook` de la API de bots, pasando la dirección del Worker y el mismo `secret_token` que `WEBHOOK_SECRET`. Lo corre el usuario en su terminal, para que el token no pase por el chat.
6. **Probar:** escribirle al bot desde la cuenta permitida (debe responder) y desde otra (debe callar).

## Esqueleto del Worker
```ts
import { Bot, webhookCallback } from "grammy";

export interface Env {
  BOT_TOKEN: string;
  BOT_INFO: string;
  WEBHOOK_SECRET: string;
  USUARIOS_PERMITIDOS: string; // "123456789,987654321"
}

export default {
  async fetch(request: Request, env: Env): Promise<Response> {
    const bot = new Bot(env.BOT_TOKEN, { botInfo: JSON.parse(env.BOT_INFO) });
    const permitidos = env.USUARIOS_PERMITIDOS.split(",").map((x) => Number(x.trim()));

    // Ignorar a cualquiera que no esté en la lista
    bot.use(async (ctx, next) => {
      if (!ctx.from || !permitidos.includes(ctx.from.id)) return;
      await next();
    });

    bot.command("start", (ctx) => ctx.reply("Hola, estoy listo."));
    bot.on("message:text", (ctx) => ctx.reply("Recibí: " + ctx.message.text));

    const atender = webhookCallback(bot, "cloudflare-mod", { secretToken: env.WEBHOOK_SECRET });
    try {
      return await atender(request);
    } catch (e) {
      // Si algo falla al contestar (por ejemplo Telegram no responde), anotar solo el motivo (nunca el mensaje)
      // y devolver 200: con un 500, Telegram reintenta el mismo mensaje muchas veces.
      // (bot.catch no sirve aquí: con webhooks, grammY deja pasar el error.)
      console.error("error del bot:", (e as Error).message);
      return new Response("ok", { status: 200 });
    }
  },
};
```

## Avisos al teléfono (el bot manda un mensaje a tu chat)
Desde un flujo o un Worker, el bot puede enviarse un mensaje a sí mismo con el método `sendMessage` de la API de bots, dirigido al número de usuario del dueño. Es gratis y no necesita otra aplicación. Ver también `apis-gratis`.

## Qué se probó y qué no
- **Probado** (sin internet, con grammY y llamadas a Telegram simuladas): la lista de permitidos responde a un usuario permitido y ignora a uno desconocido, y el comando `/start` responde.
- **Probado el 2026-11-04** con el esqueleto de arriba corriendo en el motor local de Cloudflare (`wrangler dev` 4.157, grammY con `cloudflare-mod`, `botInfo` y `secretToken`): sin la clave secreta o con una equivocada, el Worker responde **401** y no procesa nada; con la clave correcta y un usuario que no está en la lista, responde 200 y no contesta; con la clave y un usuario permitido, intenta contestar con `sendMessage` (en la prueba falló solo porque no había salida a Telegram). Cualquier petición sin la clave, incluso un GET, da 401.
- **Probado el 2026-11-06** (wrangler 4.158.0, grammY 1.46.0, Worker local real) con `probar_webhook.py`: 7 de 7. Esa prueba encontró un fallo del esqueleto anterior: si Telegram no respondía al enviar el mensaje, el Worker daba **500** (Telegram habría reintentado). Se arregló con el `try/catch` de arriba; `bot.catch` **no** sirve con webhooks (se probó y seguía dando 500).
- **No probado:** el Worker publicado en Cloudflare, el registro real del webhook con `setWebhook` y una conversación real con Telegram (necesitan un token real, que se queda en manos del usuario). Ojo: si Telegram no responde y el Worker da 500, Telegram reintenta el mensaje varias veces.

## Datos de la guía oficial de webhooks de Telegram [F]
(core.telegram.org/bots/webhooks, consultada el 2026-11-06.) Puertos permitidos: 443, 80, 88 y 8443. Solo IPv4. Exige TLS 1.2 o más. Telegram envía desde `149.154.160.0/20` y `91.108.4.0/22` (la guía avisa que pueden cambiar). Cloudflare Workers ya cumple todo esto; **no hace falta filtrar por IP**: el `secret_token` ya identifica a Telegram, y filtrar por una lista que puede cambiar solo agrega fallos.

## Probar el bot corriendo (con mensajes falsos)
Con el bot en marcha en tu computador (`wrangler dev`, con claves de prueba inventadas en `.dev.vars`, nunca las reales):
```
python -I skills\seguridad-agentes\scripts\probar_webhook.py telegram http://127.0.0.1:8787/ --secreto CLAVE-DE-PRUEBA --permitido 111111111
```
Comprueba 7 cosas: rechaza sin clave y con clave equivocada, rechaza un GET, no responde a usuarios fuera de la lista, y **no devuelve 5xx** ni con usuario permitido, ni con cuerpo roto, ni con cuerpo enorme (un 5xx hace que Telegram reintente el mismo mensaje). Ver `seguridad-agentes`.

## Revisar el bot
Antes de publicar: `python -I skills\seguridad-agentes\scripts\revisar_bot.py CARPETA-DEL-BOT` (ver `seguridad-agentes`). Comprueba `secret_token`, lista de usuarios y que no haya claves escritas. Se probó con este mismo esqueleto: sale sin hallazgos graves.

## Señales de alerta
- El token pegado en el chat, en el código o en un archivo del repositorio.
- Un bot que responde a cualquiera.
- Un webhook sin clave secreta.
- Un bot que ejecuta lo que le escriben sin pedir confirmación.

## Verificación
- [ ] El token y la clave del webhook están como secretos.
- [ ] Solo los usuarios de la lista reciben respuesta.
- [ ] El webhook usa `secret_token`.
- [ ] Se probó con una cuenta permitida y con una que no.
