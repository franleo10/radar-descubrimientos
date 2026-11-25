// GET /api/stats?slug=...  -> votos, confirmaciones, comentarios y lo que ya votó esta persona.
import { counts, ensureSchema, json, SLUG_RE, voterId } from "../_lib.js";

// Con esta cantidad de reportes de personas distintas, el comentario se oculta hasta que lo revises.
const HIDE_AT = 3;

export async function onRequestGet({ request, env }) {
  const slug = new URL(request.url).searchParams.get("slug") || "";
  if (!SLUG_RE.test(slug)) return json({ error: "Guía inválida" }, 400);
  const voter = await voterId(request, env);
  await ensureSchema(env);
  const [c, mine, conf, comments] = await Promise.all([
    counts(env, slug),
    env.DB.prepare("SELECT kind FROM reactions WHERE slug = ? AND voter = ?").bind(slug, voter).first(),
    env.DB.prepare("SELECT 1 AS ok FROM confirms WHERE slug = ? AND voter = ?").bind(slug, voter).first(),
    env.DB.prepare(
      `SELECT c.id, c.name, c.body, c.created FROM comments c
       WHERE c.slug = ?1 AND (SELECT COUNT(*) FROM reports r WHERE r.comment_id = c.id) < ?2
       ORDER BY c.created DESC LIMIT 100`).bind(slug, HIDE_AT).all(),
  ]);
  return json({ ...c, mine: mine?.kind || null, confirmed: !!conf, comments: comments.results });
}
