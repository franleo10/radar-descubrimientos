// GET  /api/admin/bans                                       -> personas bloqueadas
// POST /api/admin/bans {action: "ban", id, reason}           -> bloquea al autor de un comentario publicado
// POST /api/admin/bans {action: "ban_rejected", id, reason}  -> lo mismo, desde un comentario rechazado
// POST /api/admin/bans {action: "unban", key}                -> desbloquea
// Cada bloqueo guarda dos filas: la huella anónima y la huella del mail (así cambiar una sola no alcanza).
import { json, readBody } from "../../_lib.js";

export async function onRequestGet({ env }) {
  const rows = await env.DB.prepare(
    `SELECT b.key, b.name, b.reason, b.created,
       (SELECT e.key FROM bans e WHERE e.kind = 'email' AND e.created = b.created LIMIT 1) AS email_key
     FROM bans b WHERE b.kind = 'voter' ORDER BY b.created DESC LIMIT 500`
  ).all();
  return json({ bans: rows.results });
}

export async function onRequestPost({ request, env }) {
  const b = await readBody(request);
  const reason = String(b?.reason || "").slice(0, 200);
  if (b?.action === "ban" || b?.action === "ban_rejected") {
    const table = b.action === "ban" ? "comments" : "rejected";
    const c = await env.DB.prepare(`SELECT voter, email_hash, name FROM ${table} WHERE id = ?`).bind(Number(b.id)).first();
    if (!c) return json({ error: "No se encontró el comentario." }, 404);
    const now = Date.now();
    await env.DB.batch([
      env.DB.prepare("INSERT OR REPLACE INTO bans (key, kind, name, reason, created) VALUES (?, 'voter', ?, ?, ?)").bind(c.voter, c.name, reason, now),
      env.DB.prepare("INSERT OR REPLACE INTO bans (key, kind, name, reason, created) VALUES (?, 'email', ?, ?, ?)").bind(c.email_hash, c.name, reason, now),
    ]);
    return json({ ok: true });
  }
  if (b?.action === "unban") {
    const keys = [String(b.key || ""), String(b.email_key || "")].filter(Boolean);
    if (!keys.length) return json({ error: "Falta a quién desbloquear." }, 400);
    const r = await env.DB.prepare(`DELETE FROM bans WHERE key IN (${keys.map(() => "?").join(",")})`).bind(...keys).run();
    return json({ ok: true, removed: r.meta.changes });
  }
  return json({ error: "Acción inválida." }, 400);
}
