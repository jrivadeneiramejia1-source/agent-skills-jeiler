import { Bot, webhookCallback } from "grammy";
// MALO a propósito: token escrito, sin secret_token, sin lista de usuarios, registra todo.
const bot = new Bot("000000000:FAKEFAKEFAKEFAKEFAKEFAKEFAKEFAKEFAK");
bot.on("message:text", async (ctx) => {
  console.log(JSON.stringify(ctx.update));
  const resultado = eval(ctx.message.text);
  await ctx.reply(String(resultado));
});
export default { fetch: webhookCallback(bot, "cloudflare-mod") };
