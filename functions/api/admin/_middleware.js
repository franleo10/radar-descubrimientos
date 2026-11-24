// Todo /api/admin/* pide la contraseña del panel (variable secreta ADMIN_TOKEN en Cloudflare).
// Se manda en el encabezado "Authorization: Bearer <contraseña>".
import { ensureSchema, json } from "../../_lib.js";

async function digest(text) {
  return new Uint8Array(await crypto.subtle.digest("SHA-256", new TextEncoder().encode(text)));
}

// Compara sin cortar antes (así el tiempo de respuesta no da pistas).
async function same(a, b) {
  const [x, y] = await Promise.all([digest(a), digest(b)]);
  let diff = 0;
  for (let i = 0; i < x.length; i++) diff |= x[i] ^ y[i];
  return diff === 0;
}

export async function onRequest({ request, env, next }) {
  if (!env.ADMIN_TOKEN || env.ADMIN_TOKEN.length < 16) {
    return json({ error: "El panel no está configurado: falta la variable secreta ADMIN_TOKEN (16 caracteres o más)." }, 503);
  }
  const given = (request.headers.get("authorization") || "").replace(/^Bearer\s+/i, "");
  if (!given || !(await same(given, env.ADMIN_TOKEN))) {
    await new Promise((r) => setTimeout(r, 400)); // frena a quien prueba contraseñas
    return json({ error: "Contraseña incorrecta." }, 401);
  }
  await ensureSchema(env);
  const res = await next();
  const out = new Response(res.body, res);
  out.headers.set("cache-control", "no-store");
  out.headers.set("x-robots-tag", "noindex");
  return out;
}
