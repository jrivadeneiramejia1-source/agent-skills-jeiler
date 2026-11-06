import { firmaValida } from "./firma.mjs";

export interface Env {
  APP_SECRET: string;
  VERIFY_TOKEN: string;
  NUMEROS_PERMITIDOS: string; // "570000000000" (inventado)
  VISTOS: KVNamespace;        // para no procesar dos veces el mismo mensaje
}

export default {
  async fetch(request: Request, env: Env): Promise<Response> {
    const url = new URL(request.url);
    if (request.method === "GET") {
      // Verificación del webhook: Meta manda hub.mode, hub.verify_token y hub.challenge
      if (url.searchParams.get("hub.mode") === "subscribe" &&
          url.searchParams.get("hub.verify_token") === env.VERIFY_TOKEN) {
        return new Response(url.searchParams.get("hub.challenge") ?? "", { status: 200 });
      }
      return new Response("no", { status: 403 });
    }
    const cuerpo = await request.text();
    if (!(await firmaValida(cuerpo, request.headers.get("x-hub-signature-256"), env.APP_SECRET))) {
      return new Response("firma inválida", { status: 401 });
    }
    const permitidos = env.NUMEROS_PERMITIDOS.split(",");
    const msg = JSON.parse(cuerpo)?.entry?.[0]?.changes?.[0]?.value?.messages?.[0];
    if (msg && permitidos.includes(msg.from) && !(await env.VISTOS.get(msg.id))) {
      await env.VISTOS.put(msg.id, "1", { expirationTtl: 86400 });
      // ... aquí va la lógica del bot
    }
    return new Response("ok", { status: 200 }); // responder rápido: Meta reintenta si tarda
  },
};
