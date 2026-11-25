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

// Tablas que agregó el panel de administración. Se crean solas la primera vez (no hace falta migrar).
const EXTRA_SCHEMA = [
  `CREATE TABLE IF NOT EXISTS bans (
     key     TEXT PRIMARY KEY,
     kind    TEXT NOT NULL,
     name    TEXT NOT NULL DEFAULT '',
     reason  TEXT NOT NULL DEFAULT '',
     created INTEGER NOT NULL
   )`,
  `CREATE TABLE IF NOT EXISTS rejected (
     id         INTEGER PRIMARY KEY AUTOINCREMENT,
     slug       TEXT NOT NULL,
     name       TEXT NOT NULL,
     email_hash TEXT NOT NULL,
     body       TEXT NOT NULL,
     reason     TEXT NOT NULL,
     voter      TEXT NOT NULL,
     created    INTEGER NOT NULL
   )`,
  "CREATE INDEX IF NOT EXISTS rejected_by_created ON rejected (created)",
  `CREATE TABLE IF NOT EXISTS removed (
     slug    TEXT PRIMARY KEY,
     title   TEXT NOT NULL DEFAULT '',
     reason  TEXT NOT NULL DEFAULT '',
     created INTEGER NOT NULL
   )`,
  "CREATE TABLE IF NOT EXISTS presence (voter TEXT PRIMARY KEY, seen INTEGER NOT NULL)",
  `CREATE TABLE IF NOT EXISTS reports (
     comment_id INTEGER NOT NULL,
     voter      TEXT NOT NULL,
     reason     TEXT NOT NULL DEFAULT '',
     created    INTEGER NOT NULL,
     PRIMARY KEY (comment_id, voter)
   )`,
];
let schemaReady = false;
export async function ensureSchema(env) {
  if (schemaReady) return;
  await env.DB.batch(EXTRA_SCHEMA.map((s) => env.DB.prepare(s)));
  schemaReady = true;
}

// ¿Esta persona tiene prohibido comentar? Se mira la huella anónima (voter) y la del mail.
// En bans, "key" es una de las dos huellas y "kind" dice cuál ("voter" o "email").
export async function isBanned(env, voter, mailHash) {
  await ensureSchema(env);
  const r = await env.DB.prepare("SELECT 1 AS b FROM bans WHERE key IN (?, ?) LIMIT 1").bind(voter, mailHash).first();
  return !!r;
}
