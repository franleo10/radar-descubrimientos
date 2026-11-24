// GET  /api/admin/comments?before=<ms>&q=<texto>&slug=<guía>&voter=<huella>  -> últimos comentarios publicados
// POST /api/admin/comments {action: "delete", id}         -> borra un comentario
// POST /api/admin/comments {action: "delete_author", id}  -> borra todos los de esa persona
import { json, readBody } from "../../_lib.js";

const PAGE = 50;

export async function onRequestGet({ request, env }) {
  const u = new URL(request.url).searchParams;
  const where = ["c.created < ?1"], args = [Number(u.get("before")) || Date.now() + 1];
  const add = (sql, v) => { args.push(v); where.push(sql.replaceAll("?", `?${args.length}`)); };
  if (u.get("q")) add("(c.body LIKE ? OR c.name LIKE ?)", `%${u.get("q").slice(0, 80)}%`);
  if (u.get("slug")) add("c.slug = ?", u.get("slug").slice(0, 90));
  if (u.get("voter")) add("c.voter = ?", u.get("voter").slice(0, 64));
  const rows = await env.DB.prepare(
    `SELECT c.id, c.slug, c.name, c.body, c.created, c.voter,
       (SELECT COUNT(*) FROM comments x WHERE x.voter = c.voter) AS by_voter,
       EXISTS (SELECT 1 FROM bans b WHERE b.key IN (c.voter, c.email_hash)) AS banned
     FROM comments c WHERE ${where.join(" AND ")} ORDER BY c.created DESC LIMIT ${PAGE}`
  ).bind(...args).all();
  return json({ comments: rows.results, more: rows.results.length === PAGE });
}

export async function onRequestPost({ request, env }) {
  const b = await readBody(request);
  const id = Number(b?.id);
  if (!Number.isInteger(id)) return json({ error: "Falta el comentario." }, 400);
  if (b.action === "delete") {
    const r = await env.DB.prepare("DELETE FROM comments WHERE id = ?").bind(id).run();
    return json({ ok: true, deleted: r.meta.changes });
  }
  if (b.action === "delete_author") {
    const c = await env.DB.prepare("SELECT voter FROM comments WHERE id = ?").bind(id).first();
    if (!c) return json({ error: "Ese comentario ya no existe." }, 404);
    const r = await env.DB.prepare("DELETE FROM comments WHERE voter = ?").bind(c.voter).run();
    return json({ ok: true, deleted: r.meta.changes });
  }
  return json({ error: "Acción inválida." }, 400);
}
