// MALO a propósito: no comprueba la firma, responde el challenge sin verificar el token.
export default {
  async fetch(request: Request): Promise<Response> {
    const url = new URL(request.url);
    if (request.method === "GET") return new Response(url.searchParams.get("hub.challenge") ?? "");
    const body = await request.json();
    console.log(JSON.stringify(body));
    await fetch("https://graph.facebook.com/v20.0/123/messages", { method: "POST", body: "{}" });
    return new Response("ok");
  },
};
