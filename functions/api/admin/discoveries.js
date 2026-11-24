// GET  /api/admin/discoveries                                   -> descubrimientos quitados
// POST /api/admin/discoveries {action: "remove", slug, title, reason}  -> quitar uno
// POST /api/admin/discoveries {action: "restore", slug}         -> volver a publicarlo
//
// Quitar tiene efecto en dos pasos: la página deja de verse al instante (functions/_middleware.js)
// y en la próxima corrida el bot lo saca de los datos y lo guarda aparte (bot/removed.py).
import { json, readBody, SLUG_RE } from "../../_lib.js";
import { forgetRemovedCache } from "../../_middleware.js";

export async function onRequestGet({ env }) {
  const rows = await env.DB.prepare("SELECT slug, title, reason, created FROM removed ORDER BY created DESC").all();
  return json({ removed: rows.results });
}

export async function onRequestPost({ request, env }) {
  const b = await readBody(request);
  const slug = String(b?.slug || "");
  if (!SLUG_RE.test(slug)) return json({ error: "Descubrimiento inválido." }, 400);
  if (b.action === "remove") {
    await env.DB.prepare("INSERT OR REPLACE INTO removed (slug, title, reason, created) VALUES (?, ?, ?, ?)")
      .bind(slug, String(b.title || "").slice(0, 200), String(b.reason || "").slice(0, 200), Date.now()).run();
    forgetRemovedCache();
    return json({ ok: true });
  }
  if (b.action === "restore") {
    const r = await env.DB.prepare("DELETE FROM removed WHERE slug = ?").bind(slug).run();
    forgetRemovedCache();
    return json({ ok: true, restored: r.meta.changes });
  }
  return json({ error: "Acción inválida." }, 400);
}
