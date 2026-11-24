// GET /api/admin/overview -> números generales, actividad por día y las guías con más movimiento.
import { json } from "../../_lib.js";

const DAY = 86400_000;

export async function onRequestGet({ env }) {
  const now = Date.now(), d1 = now - DAY, d7 = now - 7 * DAY, d14 = now - 14 * DAY;
  const q = (sql, ...args) => env.DB.prepare(sql).bind(...args);
  const [totals, perDay, top, disliked, online, perSlug] = await env.DB.batch([
    q(`SELECT
         (SELECT COUNT(*) FROM comments) AS comments,
         (SELECT COUNT(*) FROM comments WHERE created > ?1) AS comments_24h,
         (SELECT COUNT(*) FROM comments WHERE created > ?2) AS comments_7d,
         (SELECT COUNT(*) FROM rejected WHERE created > ?1) AS rejected_24h,
         (SELECT COUNT(*) FROM rejected WHERE created > ?2) AS rejected_7d,
         (SELECT COUNT(*) FROM reactions) AS votes,
         (SELECT COUNT(*) FROM reactions WHERE created > ?1) AS votes_24h,
         (SELECT COUNT(*) FROM reactions WHERE created > ?2) AS votes_7d,
         (SELECT COUNT(*) FROM confirms) AS confirms,
         (SELECT COUNT(*) FROM confirms WHERE created > ?2) AS confirms_7d,
         (SELECT COUNT(*) FROM (
            SELECT voter FROM reactions WHERE created > ?2 UNION SELECT voter FROM confirms WHERE created > ?2
            UNION SELECT voter FROM comments WHERE created > ?2)) AS people_7d,
         (SELECT COUNT(*) FROM bans WHERE kind = 'voter') AS bans`, d1, d7),
    q(`SELECT day, SUM(c) AS comments, SUM(v) AS votes, SUM(r) AS rejected FROM (
         SELECT (created / 86400000) AS day, 1 AS c, 0 AS v, 0 AS r FROM comments WHERE created > ?1
         UNION ALL SELECT (created / 86400000), 0, 1, 0 FROM reactions WHERE created > ?1
         UNION ALL SELECT (created / 86400000), 0, 1, 0 FROM confirms WHERE created > ?1
         UNION ALL SELECT (created / 86400000), 0, 0, 1 FROM rejected WHERE created > ?1
       ) GROUP BY day ORDER BY day`, d14),
    q(`SELECT slug, SUM(l) AS likes, SUM(dl) AS dislikes, SUM(cf) AS confirms, SUM(cm) AS comments FROM (
         SELECT slug, kind = 'like' AS l, kind = 'dislike' AS dl, 0 AS cf, 0 AS cm FROM reactions WHERE created > ?1
         UNION ALL SELECT slug, 0, 0, 1, 0 FROM confirms WHERE created > ?1
         UNION ALL SELECT slug, 0, 0, 0, 1 FROM comments WHERE created > ?1
       ) GROUP BY slug ORDER BY (likes + confirms + comments * 2) DESC LIMIT 10`, d7),
    q(`SELECT slug, SUM(kind = 'like') AS likes, SUM(kind = 'dislike') AS dislikes
       FROM reactions GROUP BY slug HAVING dislikes >= 2 AND dislikes > likes
       ORDER BY dislikes DESC LIMIT 10`),
    q("SELECT COUNT(*) AS n FROM presence WHERE seen > ?", Math.floor(now / 1000) - 120),
    q(`SELECT slug, SUM(l) AS likes, SUM(dl) AS dislikes, SUM(cf) AS confirms, SUM(cm) AS comments FROM (
         SELECT slug, kind = 'like' AS l, kind = 'dislike' AS dl, 0 AS cf, 0 AS cm FROM reactions
         UNION ALL SELECT slug, 0, 0, 1, 0 FROM confirms
         UNION ALL SELECT slug, 0, 0, 0, 1 FROM comments
       ) GROUP BY slug`),
  ]);
  return json({
    perSlug: Object.fromEntries(perSlug.results.map(({ slug, ...r }) => [slug, r])),
    totals: { ...totals.results[0], online: online.results[0].n },
    perDay: perDay.results.map((r) => ({ ...r, day: new Date(r.day * DAY).toISOString().slice(0, 10) })),
    top: top.results,
    disliked: disliked.results,
  });
}
