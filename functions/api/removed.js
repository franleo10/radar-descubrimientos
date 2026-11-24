// GET /api/removed -> slugs de los descubrimientos quitados desde el panel.
// Lo usa el bot para sacarlos de los datos (y devolverlos si se restauran). No tiene nada privado.
import { ensureSchema, json } from "../_lib.js";

export async function onRequestGet({ env }) {
  await ensureSchema(env);
  const rows = await env.DB.prepare("SELECT slug FROM removed").all();
  return json({ removed: rows.results.map((r) => r.slug) });
}
