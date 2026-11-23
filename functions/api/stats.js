// GET /api/stats?slug=...  -> votos, confirmaciones, comentarios y lo que ya votó esta persona.
import { counts, json, SLUG_RE, voterId } from "../_lib.js";

export async function onRequestGet({ request, env }) {
  const slug = new URL(request.url).searchParams.get("slug") || "";
  if (!SLUG_RE.test(slug)) return json({ error: "Guía inválida" }, 400);
  const voter = await voterId(request, env);
  const [c, mine, conf, comments] = await Promise.all([
    counts(env, slug),
    env.DB.prepare("SELECT kind FROM reactions WHERE slug = ? AND voter = ?").bind(slug, voter).first(),
    env.DB.prepare("SELECT 1 AS ok FROM confirms WHERE slug = ? AND voter = ?").bind(slug, voter).first(),
    env.DB.prepare("SELECT name, body, created FROM comments WHERE slug = ? ORDER BY created DESC LIMIT 100")
      .bind(slug).all(),
  ]);
  return json({ ...c, mine: mine?.kind || null, confirmed: !!conf, comments: comments.results });
}
