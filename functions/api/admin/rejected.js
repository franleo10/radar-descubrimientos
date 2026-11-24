// GET  /api/admin/rejected?before=<ms>              -> comentarios que la moderación automática no publicó
// POST /api/admin/rejected {action: "approve", id}  -> publicarlo igual (si la moderación se equivocó)
// POST /api/admin/rejected {action: "dismiss", id}  -> sacarlo de la lista
import { json, readBody } from "../../_lib.js";

const PAGE = 50;

export async function onRequestGet({ request, env }) {
  const before = Number(new URL(request.url).searchParams.get("before")) || Date.now() + 1;
  const rows = await env.DB.prepare(
    `SELECT r.id, r.slug, r.name, r.body, r.reason, r.created, r.voter,
       EXISTS (SELECT 1 FROM bans b WHERE b.key IN (r.voter, r.email_hash)) AS banned
     FROM rejected r WHERE r.created < ? ORDER BY r.created DESC LIMIT ${PAGE}`
  ).bind(before).all();
  return json({ rejected: rows.results, more: rows.results.length === PAGE });
}

export async function onRequestPost({ request, env }) {
  const b = await readBody(request);
  const id = Number(b?.id);
  if (!Number.isInteger(id)) return json({ error: "Falta el comentario." }, 400);
  if (b.action === "approve") {
    const r = await env.DB.prepare("SELECT * FROM rejected WHERE id = ?").bind(id).first();
    if (!r) return json({ error: "Ya no está en la lista." }, 404);
    await env.DB.batch([
      env.DB.prepare("INSERT INTO comments (slug, name, email_hash, body, voter, created) VALUES (?, ?, ?, ?, ?, ?)")
        .bind(r.slug, r.name, r.email_hash, r.body, r.voter, r.created),
      env.DB.prepare("DELETE FROM rejected WHERE id = ?").bind(id),
    ]);
    return json({ ok: true });
  }
  if (b.action === "dismiss") {
    await env.DB.prepare("DELETE FROM rejected WHERE id = ?").bind(id).run();
    return json({ ok: true });
  }
  return json({ error: "Acción inválida." }, 400);
}
