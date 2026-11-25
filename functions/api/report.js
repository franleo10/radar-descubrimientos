// POST /api/report {id, reason}  -> reportar un comentario. Una vez por persona y comentario.
// Con 3 reportes de personas distintas el comentario se oculta hasta que lo revisás en el panel.
import { ensureSchema, json, readBody, voterId } from "../_lib.js";

const MAX_PER_HOUR = 20;
const REASONS = new Set(["spam", "ofensivo", "sexual", "otro"]);

export async function onRequestPost({ request, env }) {
  const b = await readBody(request);
  const id = Number(b?.id);
  if (!Number.isInteger(id) || id < 1) return json({ error: "Comentario inválido." }, 400);
  const reason = REASONS.has(b?.reason) ? b.reason : "otro";
  await ensureSchema(env);
  const voter = await voterId(request, env);
  const [exists, recent] = await env.DB.batch([
    env.DB.prepare("SELECT 1 AS ok FROM comments WHERE id = ?").bind(id),
    env.DB.prepare("SELECT COUNT(*) AS n FROM reports WHERE voter = ? AND created > ?").bind(voter, Date.now() - 3600_000),
  ]);
  if (!exists.results.length) return json({ error: "Ese comentario ya no existe." }, 404);
  if (recent.results[0].n >= MAX_PER_HOUR) return json({ error: "Reportaste muchos comentarios seguidos. Probá en un rato." }, 429);
  await env.DB.prepare("INSERT OR IGNORE INTO reports (comment_id, voter, reason, created) VALUES (?, ?, ?, ?)")
    .bind(id, voter, reason, Date.now()).run();
  return json({ ok: true });
}
