// GET  /api/admin/reports                         -> comentarios reportados, con cuántos reportes y por qué
// POST /api/admin/reports {action: "dismiss", id}  -> el comentario está bien: se borran sus reportes
// POST /api/admin/reports {action: "delete", id}   -> se borra el comentario (y sus reportes)
// Para bloquear al autor se usa /api/admin/bans {action: "ban", id}.
import { json, readBody } from "../../_lib.js";

export async function onRequestGet({ env }) {
  const rows = await env.DB.prepare(
    `SELECT c.id, c.slug, c.name, c.body, c.created, c.voter,
       COUNT(r.voter) AS reports, MAX(r.created) AS last_report,
       GROUP_CONCAT(DISTINCT r.reason) AS reasons,
       EXISTS (SELECT 1 FROM bans b WHERE b.key IN (c.voter, c.email_hash)) AS banned
     FROM reports r JOIN comments c ON c.id = r.comment_id
     GROUP BY c.id ORDER BY reports DESC, last_report DESC LIMIT 200`
  ).all();
  return json({ reported: rows.results });
}

export async function onRequestPost({ request, env }) {
  const b = await readBody(request);
  const id = Number(b?.id);
  if (!Number.isInteger(id)) return json({ error: "Falta el comentario." }, 400);
  if (b.action === "dismiss") {
    await env.DB.prepare("DELETE FROM reports WHERE comment_id = ?").bind(id).run();
    return json({ ok: true });
  }
  if (b.action === "delete") {
    await env.DB.batch([
      env.DB.prepare("DELETE FROM comments WHERE id = ?").bind(id),
      env.DB.prepare("DELETE FROM reports WHERE comment_id = ?").bind(id),
    ]);
    return json({ ok: true });
  }
  return json({ error: "Acción inválida." }, 400);
}
