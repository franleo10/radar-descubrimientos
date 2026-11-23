// GET /api/summary -> totales por guía (lo usa el bot para confirmar guías con votos de la gente).
import { json } from "../_lib.js";

export async function onRequestGet({ env }) {
  const rows = await env.DB.prepare(
    `SELECT slug,
       SUM(kind = 'like') AS likes, SUM(kind = 'dislike') AS dislikes, 0 AS confirms
     FROM reactions GROUP BY slug
     UNION ALL
     SELECT slug, 0, 0, COUNT(*) FROM confirms GROUP BY slug`
  ).all();
  const out = {};
  for (const r of rows.results) {
    const o = (out[r.slug] ||= { likes: 0, dislikes: 0, confirms: 0 });
    o.likes += r.likes; o.dislikes += r.dislikes; o.confirms += r.confirms;
  }
  return json(out, 200, { "cache-control": "public, max-age=300" });
}
