// POST /api/react  {slug, kind: "like" | "dislike" | "none"}  -> un voto por persona y guía.
// POST /api/react  {slug, confirm: true}  -> "Me funcionó" (no se puede repetir).
import { counts, json, readBody, slugExists, voterId } from "../_lib.js";

export async function onRequestPost({ request, env }) {
  const body = await readBody(request);
  const slug = body?.slug || "";
  if (!(await slugExists(env, slug))) return json({ error: "Guía inválida" }, 400);
  const voter = await voterId(request, env);
  const now = Date.now();

  if (body.confirm === true) {
    await env.DB.prepare("INSERT OR IGNORE INTO confirms (slug, voter, created) VALUES (?, ?, ?)")
      .bind(slug, voter, now).run();
  } else if (body.kind === "like" || body.kind === "dislike") {
    await env.DB.prepare(
      `INSERT INTO reactions (slug, voter, kind, created) VALUES (?, ?, ?, ?)
       ON CONFLICT (slug, voter) DO UPDATE SET kind = excluded.kind, created = excluded.created`
    ).bind(slug, voter, body.kind, now).run();
  } else if (body.kind === "none") {
    await env.DB.prepare("DELETE FROM reactions WHERE slug = ? AND voter = ?").bind(slug, voter).run();
  } else {
    return json({ error: "Voto inválido" }, 400);
  }
  return json(await counts(env, slug));
}
