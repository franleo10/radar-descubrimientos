// POST /api/online  -> "sigo acá" de quien tiene la página abierta; devuelve cuánta gente hay ahora.
// Cada persona es su huella anónima (no la IP), así varias pestañas cuentan una sola vez.
// Se considera online a quien avisó en los últimos 2 minutos.
import { json, voterId } from "../_lib.js";

const WINDOW = 120; // segundos
const SCHEMA = `CREATE TABLE IF NOT EXISTS presence (
  voter TEXT PRIMARY KEY,
  seen  INTEGER NOT NULL
)`;

async function beat(env, voter, now) {
  const [, total] = await env.DB.batch([
    env.DB.prepare("INSERT INTO presence (voter, seen) VALUES (?1, ?2) ON CONFLICT (voter) DO UPDATE SET seen = ?2")
      .bind(voter, now),
    env.DB.prepare("SELECT COUNT(*) AS n FROM presence WHERE seen > ?").bind(now - WINDOW),
  ]);
  return total.results[0].n;
}

export async function onRequestPost({ request, env, waitUntil }) {
  const now = Math.floor(Date.now() / 1000);
  const voter = await voterId(request, env);
  let n;
  try {
    n = await beat(env, voter, now);
  } catch (err) {
    if (!String(err).includes("no such table")) return json({ error: "No disponible" }, 503);
    await env.DB.prepare(SCHEMA).run();
    n = await beat(env, voter, now);
  }
  // De vez en cuando se borra a quien se fue hace rato, para que la tabla no crezca.
  if (Math.random() < 0.05) {
    waitUntil(env.DB.prepare("DELETE FROM presence WHERE seen < ?").bind(now - 600).run());
  }
  return json({ online: n });
}
