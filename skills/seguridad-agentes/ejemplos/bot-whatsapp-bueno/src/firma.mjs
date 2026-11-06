// Comprueba X-Hub-Signature-256 con HMAC-SHA256 y el secreto de la app de Meta.
// Devuelve true solo si la firma es válida. Usa comparación de tiempo constante (crypto.subtle.verify).
export async function firmaValida(cuerpoTexto, encabezado, appSecret) {
  if (!encabezado || !encabezado.startsWith("sha256=") || !appSecret) return false;
  const hex = encabezado.slice(7);
  if (!/^[0-9a-f]{64}$/i.test(hex)) return false;
  const firma = new Uint8Array(hex.match(/../g).map((b) => parseInt(b, 16)));
  const clave = await crypto.subtle.importKey("raw", new TextEncoder().encode(appSecret),
    { name: "HMAC", hash: "SHA-256" }, false, ["verify"]);
  return crypto.subtle.verify("HMAC", clave, firma, new TextEncoder().encode(cuerpoTexto));
}
