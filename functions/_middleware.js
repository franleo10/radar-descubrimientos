// Descubrimientos quitados desde el panel: su página responde "410 Gone" al instante,
// sin esperar a que el bot regenere el sitio. Solo mira las rutas /d/, /pt/d/ y /en/d/.
import { ensureSchema } from "./_lib.js";

const DETAIL = /^\/(?:pt\/|en\/)?d\/([a-z0-9-]{3,90})\/?$/;
const TTL = 60_000; // la lista se vuelve a leer como mucho una vez por minuto
let cache = { at: 0, slugs: new Set() };

async function removedSlugs(env) {
  if (Date.now() - cache.at < TTL) return cache.slugs;
  try {
    await ensureSchema(env);
    const rows = await env.DB.prepare("SELECT slug FROM removed").all();
    cache = { at: Date.now(), slugs: new Set(rows.results.map((r) => r.slug)) };
  } catch {
    cache.at = Date.now(); // si la base falla, el sitio sigue funcionando igual
  }
  return cache.slugs;
}

// El panel avisa cuando quita o restaura, así este mismo servidor no espera el minuto.
export function forgetRemovedCache() {
  cache.at = 0;
}

const GONE = `<!doctype html><html lang="es"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1"><meta name="robots" content="noindex">
<title>Descubrimiento quitado · WastedMap</title><link rel="stylesheet" href="/site.css"></head>
<body><main class="page"><div class="wrap" style="padding:12vh 16px;text-align:center">
<h1>Este descubrimiento ya no está</h1>
<p class="lead">Lo sacamos del sitio porque no era correcto o estaba repetido.</p>
<p><a class="btn primary" href="/">Ver todos los secretos</a></p>
</div></main></body></html>`;

export async function onRequest({ request, env, next }) {
  const m = new URL(request.url).pathname.match(DETAIL);
  if (m && env.DB && (await removedSlugs(env)).has(m[1])) {
    return new Response(GONE, {
      status: 410,
      headers: { "content-type": "text/html; charset=utf-8", "cache-control": "no-store", "x-robots-tag": "noindex" },
    });
  }
  return next();
}
