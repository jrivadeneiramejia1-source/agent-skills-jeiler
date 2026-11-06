import { Bot, webhookCallback } from "grammy";

export interface Env {
  BOT_TOKEN: string;
  BOT_INFO: string;
  WEBHOOK_SECRET: string;
  USUARIOS_PERMITIDOS: string; // "111111111,222222222" (números inventados)
}

export default {
  async fetch(request: Request, env: Env): Promise<Response> {
    const bot = new Bot(env.BOT_TOKEN, { botInfo: JSON.parse(env.BOT_INFO) });
    const permitidos = env.USUARIOS_PERMITIDOS.split(",").map((x) => Number(x.trim()));

    bot.use(async (ctx, next) => {
      if (!ctx.from || !permitidos.includes(ctx.from.id)) return;
      await next();
    });
    bot.command("start", (ctx) => ctx.reply("Hola, estoy listo."));
    bot.on("message:text", (ctx) => ctx.reply("Recibí: " + ctx.message.text));

    return webhookCallback(bot, "cloudflare-mod", { secretToken: env.WEBHOOK_SECRET })(request);
  },
};
