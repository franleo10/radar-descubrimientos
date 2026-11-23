// Utilidades compartidas por las funciones de /api (Cloudflare Pages Functions).

export const json = (data, status = 200, extra = {}) =>
  new Response(JSON.stringify(data), {
    status,
    headers: { "content-type": "application/json; charset=utf-8", "cache-control": "no-store", ...extra },
  });

export const SLUG_RE = /^[a-z0-9-]{3,90}$/;

async function sha256(text) {
  const buf = await crypto.subtle.digest("SHA-256", new TextEncoder().encode(text));
  return [...new Uint8Array(buf)].map((b) => b.toString(16).padStart(2, "0")).join("");
}

// Identificador anónimo de quien vota o comenta: no guardamos la IP, solo esta huella.
export async function voterId(request, env) {
  const ip = request.headers.get("cf-connecting-ip") || "";
  const ua = request.headers.get("user-agent") || "";
  return (await sha256(`${ip}|${ua}|${env.TURNSTILE_SECRET || "wastedmap"}`)).slice(0, 32);
}

export const emailHash = (email) => sha256(`wastedmap|${email.trim().toLowerCase()}`);

// Solo se aceptan guías que existen de verdad en el sitio.
export async function slugExists(env, slug) {
  if (!SLUG_RE.test(slug)) return false;
  const res = await env.ASSETS.fetch(new Request(`https://wastedmap.com/d/${slug}/`));
  return res.status === 200;
}

export async function counts(env, slug) {
  const r = await env.DB.prepare(
    `SELECT
       (SELECT COUNT(*) FROM reactions WHERE slug = ?1 AND kind = 'like') AS likes,
       (SELECT COUNT(*) FROM reactions WHERE slug = ?1 AND kind = 'dislike') AS dislikes,
       (SELECT COUNT(*) FROM confirms WHERE slug = ?1) AS confirms`
  ).bind(slug).first();
  return { likes: r.likes, dislikes: r.dislikes, confirms: r.confirms };
}

export async function readBody(request) {
  try {
    return await request.json();
  } catch {
    return null;
  }
}
