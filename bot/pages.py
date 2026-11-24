"""Genera páginas HTML estáticas para que Google pueda leer e indexar todo.

- docs/d/<slug>/        una página por descubrimiento
- docs/c/<categoria>/   una página por categoría
- docs/sitemap.xml y docs/robots.txt
- la lista de enlaces dentro de docs/index.html (entre las marcas STATIC)

Los enlaces internos son relativos, así que al pasar a un dominio propio solo hay
que cambiar SITE_URL (se usa para la dirección canónica y el sitemap).
"""
from __future__ import annotations

import hashlib
import json
import re
import shutil
import unicodedata
from html import escape
from urllib.parse import quote

from . import config
from .brand import bsky_link, logo, tg_cta, tg_link
from . import home
from .mapa import AREAS, map_svg

CATS = {
    "easter_egg": ("easter-eggs", "Easter eggs"),
    "ubicacion_secreta": ("lugares-secretos", "Lugares secretos"),
    "coleccionable": ("coleccionables", "Coleccionables"),
    "vehiculo": ("vehiculos", "Vehículos"),
    "arma": ("armas", "Armas"),
    "dinero": ("dinero", "Dinero"),
    "mision": ("misiones", "Misiones"),
    "mecanica_truco": ("trucos-y-consejos", "Trucos y consejos"),
    "otro": ("otros", "Otros"),
}
CAT_COLOR = {
    "easter_egg": "#d61f69", "ubicacion_secreta": "#0c8f83", "coleccionable": "#b58105",
    "vehiculo": "#e0570b", "arma": "#c22d2d", "dinero": "#2b8a3e", "mision": "#6d45d9",
    "mecanica_truco": "#1b6fc2", "otro": "#7a7484",
}
CAT_INTRO = {
    "easter_egg": "Referencias escondidas, guiños a otros juegos y secretos que encontró la comunidad en GTA 6.",
    "ubicacion_secreta": "Lugares ocultos, habitaciones secretas y zonas difíciles de encontrar en el mapa de GTA 6.",
    "coleccionable": "Dónde encontrar los coleccionables de GTA 6 y qué se gana al juntarlos.",
    "vehiculo": "Autos, motos y vehículos raros de GTA 6: dónde aparecen y cómo conseguirlos.",
    "arma": "Armas especiales y ubicaciones de armas en GTA 6.",
    "dinero": "Formas legítimas de ganar dinero en GTA 6, sobre todo al principio del juego.",
    "mision": "Misiones secretas, golpes y cómo sacarles el máximo provecho en GTA 6.",
    "mecanica_truco": "Controles ocultos, mecánicas poco conocidas y consejos para jugar mejor a GTA 6.",
    "otro": "Otros descubrimientos de la comunidad en GTA 6.",
}


def _slugify(text: str, fallback: str = "descubrimiento") -> str:
    text = unicodedata.normalize("NFKD", text or "")
    text = re.sub(r"[^a-z0-9]+", "-", text.encode("ascii", "ignore").decode().lower()).strip("-")
    return text[:60].rstrip("-") or fallback


def slug_for(e: dict) -> str:
    return f"{_slugify(e.get('titulo'))}-{hashlib.sha1(e['id'].encode()).hexdigest()[:5]}"


def indexable(e: dict) -> bool:
    """Qué páginas van a Google. Las dudosas y flojas se ven en la web pero no se indexan.

    Entran las confirmadas, las que confirmó la comunidad y las que, aunque no estén del todo
    claras, tienen contenido propio (explicación o pasos) y respaldo (varias fuentes o un video
    muy visto). Así no mandamos a Google páginas casi vacías.
    """
    if e.get("confianza") == "alta" or e.get("confirmado_por_comunidad"):
        return True
    contenido = len(e.get("detalle") or "") >= 200 or len(e.get("pasos") or []) >= 3
    respaldo = int(e.get("popularity") or 0) >= 5000 or bool(e.get("fuentes_extra"))
    return contenido and respaldo


MIN_ZONE_ENTRIES = 1  # zonas = las grandes áreas del mapa (ver bot/mapa.py)
WEEK_DAYS = 7


def _date(iso: str) -> str:
    return f"{iso[8:10]}/{iso[5:7]}/{iso[0:4]}" if len(iso) >= 10 else ""


def _num(n) -> str:
    n = n or 0
    return f"{n / 1e6:.1f} M" if n >= 1e6 else f"{round(n / 1e3)} k" if n >= 1e3 else str(n)


def _thumb(e: dict) -> str:
    if e.get("thumbnail"):
        return e["thumbnail"]
    if e.get("video_id"):
        return f"https://i.ytimg.com/vi/{quote(e['video_id'])}/hqdefault.jpg"
    return ""


def _safe_json(data) -> str:
    return json.dumps(data, ensure_ascii=False).replace("</", "<\\/")


def _ver(name: str) -> str:
    """Huella de un archivo: cambia cuando cambia, así nadie ve versiones viejas en caché."""
    f = config.DOCS_DIR / name
    return hashlib.sha1(f.read_bytes()).hexdigest()[:8] if f.exists() else "0"


def _css_version() -> str:
    return _ver("site.css")


def _community(e: dict, root: str) -> str:
    """Votos, 'me funcionó' y comentarios (se completa con community.js)."""
    return f"""<section id="community" class="community" data-slug="{escape(e['slug'])}" data-sitekey="{escape(config.TURNSTILE_SITEKEY)}" hidden>
  <h2>¿Te sirvió?</h2>
  <div class="votes">
    <button class="vote" data-act="like" aria-pressed="false"><span>Me gusta</span> <b data-n="likes">0</b></button>
    <button class="vote" data-act="dislike" aria-pressed="false"><span>No me gusta</span> <b data-n="dislikes">0</b></button>
    <button class="vote confirm" data-act="confirm" aria-pressed="false"><span>Me funcionó</span> <b data-n="confirms">0</b></button>
  </div>
  <p class="note">"Me funcionó" ayuda a confirmar el hallazgo para el resto de la comunidad.</p>
  <h2>Comentarios <span class="c-count"></span></h2>
  <form class="c-form">
    <div class="c-row"><input name="name" maxlength="40" required placeholder="Tu nombre o apodo" autocomplete="nickname">
    <input name="email" type="email" maxlength="200" required placeholder="Tu mail (no se publica)" autocomplete="email"></div>
    <textarea name="body" maxlength="1000" required rows="3" placeholder="¿Te funcionó? ¿Encontraste algo más? Contalo acá."></textarea>
    <div class="c-captcha"></div>
    <div class="c-foot"><button class="btn primary" type="submit">Publicar comentario</button>
    <span class="c-msg"></span></div>
    <p class="note">Tu mail no se muestra ni se guarda: solo usamos una huella cifrada para frenar el spam. Los comentarios pasan por una revisión automática. <a href="{root}privacidad/">Privacidad</a>.</p>
  </form>
  <ul class="c-list"></ul>
</section>
<script src="{root}community.js?v={_ver('community.js')}" defer></script>"""


MENU = '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M4 7h16M4 12h16M4 17h16"/></svg>'


def _layout(*, title: str, description: str, canonical: str, root: str, body: str,
            image: str = "", jsonld: list | None = None, noindex: bool = False,
            bare: bool = False, og_type: str = "article", wide: bool = False,
            lang: str = "es", alternates: list | None = None) -> str:
    robots = '<meta name="robots" content="noindex, follow">' if noindex else ""
    # Sin imagen propia (inicio, categorías, zonas...) se usa la de la marca.
    og_image = f'<meta property="og:image" content="{escape(image or config.SITE_URL + "/og.png?v=2")}">'
    ld = "".join(f'<script type="application/ld+json">{_safe_json(x)}</script>' for x in (jsonld or []))
    links = (f'<a href="{root}descubrimientos/">Descubrimientos</a><a href="{root}semana/">Top de la semana</a>'
             f'<a href="{root}#categorias">Categorías</a><a href="{root}lista/">Mi lista</a>')
    alt = "".join(f'<link rel="alternate" hreflang="{h}" href="{escape(u)}">' for h, u in (alternates or []))
    if alternates:
        alt += f'<link rel="alternate" hreflang="x-default" href="{escape(alternates[0][1])}">'
    cta, foot_txt = "Abrir el mapa", ("Guía no oficial hecha por fans de GTA 6. No tiene relación con Rockstar Games ni con "
                                      "Take-Two Interactive. Los videos son de sus autores y se muestran con el reproductor original.")
    if lang == "pt":
        links = (f'<a href="{root}pt/">Início</a><a href="{root}pt/#categorias">Categorias</a>'
                 f'<a href="{root}" hreflang="es">Versão em espanhol</a>')
        cta, foot_txt = "Abrir o mapa", ("Guia não oficial feito por fãs de GTA 6. Não tem relação com a Rockstar Games nem com a "
                                         "Take-Two Interactive. Os vídeos são de seus autores e aparecem com o player original.")
    main = body if bare else f'<div class="wrap{" wide" if wide else ""}">\n{body}\n</div>'
    return f"""<!doctype html>
<html lang="{"pt-BR" if lang == "pt" else "es"}">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{escape(title)}</title>
<meta name="description" content="{escape(description)}">
<link rel="canonical" href="{escape(canonical)}">
{alt}
{robots}
<meta property="og:type" content="{og_type}">
<meta property="og:title" content="{escape(title)}">
<meta property="og:description" content="{escape(description)}">
<meta property="og:url" content="{escape(canonical)}">
{og_image}
<meta name="twitter:card" content="summary_large_image">
<link rel="sitemap" type="application/xml" href="{root}sitemap.xml">
<link rel="icon" href="{root}favicon.svg" type="image/svg+xml">
<link rel="icon" href="{root}favicon-32.png" sizes="32x32" type="image/png">
<link rel="apple-touch-icon" href="{root}apple-touch-icon.png">
<meta name="theme-color" content="#f6f3ee">
<link rel="preload" href="{root}fonts/inter.woff2" as="font" type="font/woff2" crossorigin>
<link rel="stylesheet" href="{root}site.css?v={_css_version()}">
<script>document.documentElement.classList.add("fx");setTimeout(()=>{{if(!window.wmToast)document.documentElement.classList.remove("fx")}},4000)</script>
<script src="{root}fx.js?v={_ver("fx.js")}" defer></script>
{ld}
</head>
<body>
<header class="topbar"><div class="wrap bar">
{logo(root)}
<nav class="nav" aria-label="Principal">{links}</nav>
<a class="btn primary sm map-btn" href="{root}mapa/">{cta}</a>
<details class="menu"><summary aria-label="Menú">{MENU}</summary><div class="menu-panel"><a href="{root}mapa/">Mapa</a>{links}</div></details>
</div></header>
<main class="{"home" if bare else "page"}">
{main}
</main>
<footer class="foot"><div class="wrap foot-grid">
<div class="foot-brand">{logo(root)}
<p>{foot_txt}</p></div>
<nav aria-label="Explorar"><h3>Explorar</h3><a href="{root}mapa/">Mapa</a><a href="{root}descubrimientos/">Descubrimientos</a><a href="{root}semana/">Top de la semana</a><a href="{root}lista/">Mi lista</a></nav>
<nav aria-label="WastedMap"><h3>WastedMap</h3><a href="{root}acerca/">Acerca de</a><a href="{root}privacidad/">Privacidad</a><a href="{root}contacto/">Contacto</a><a href="{root}pt/" hreflang="pt-BR">Em português</a></nav>
<nav aria-label="Redes"><h3>Seguinos</h3>{tg_link("social")}{bsky_link("social")}</nav>
</div></footer>
<script>
window.wmAgo = (scope = document) => scope.querySelectorAll("time[data-ago]").forEach(t => {{
  const h = (Date.now() - new Date(t.getAttribute("datetime"))) / 36e5;
  if (!(h >= 0)) return;
  const d = Math.floor(h / 24);
  t.textContent = h < 1 ? "hace minutos" : h < 24 ? `hace ${{Math.floor(h)}} h` : d === 1 ? "ayer" : `hace ${{d}} días`;
}});
wmAgo();
document.querySelectorAll(".done-btn").forEach(b => {{
  const KEY = "wm-hechos";
  let done; try {{ done = new Set(JSON.parse(localStorage.getItem(KEY) || "[]")); }} catch {{ done = new Set(); }}
  const paint = () => {{ const on = done.has(b.dataset.slug); b.setAttribute("aria-pressed", on); b.textContent = on ? "Hecho ✓" : "Marcar como hecho"; }};
  b.addEventListener("click", () => {{
    done.has(b.dataset.slug) ? done.delete(b.dataset.slug) : done.add(b.dataset.slug);
    try {{ localStorage.setItem(KEY, JSON.stringify([...done])); }} catch {{}}
    paint();
    if (done.has(b.dataset.slug) && window.wmToast) wmToast("¡Secreto encontrado!", "Lo sumamos a tu lista");
  }});
  paint();
}});
document.addEventListener("click", ev => {{
  const sp = ev.target.closest(".spoiler-btn");
  if (sp) {{ document.querySelectorAll(".spoiler").forEach(x => x.classList.remove("spoiler")); sp.remove(); return; }}
  const m = ev.target.closest(".media[data-yt]");
  if (m && !m.closest(".spoiler")) {{
    m.outerHTML = `<div class="media"><iframe src="https://www.youtube-nocookie.com/embed/${{encodeURIComponent(m.dataset.yt)}}?autoplay=1" allow="autoplay; encrypted-media; picture-in-picture" allowfullscreen title="Video"></iframe></div>`;
  }}
}});
</script>
</body>
</html>
"""


def _mini_card(e: dict, root: str) -> str:
    thumb = _thumb(e)
    img = f'<img loading="lazy" src="{escape(thumb)}" alt="">' if thumb else ""
    cls = " spoiler-mini" if e.get("spoiler") else ""
    return (f'<a class="mini{cls}" href="{root}d/{e["slug"]}/">{img}'
            f'<span>{escape(e.get("titulo", ""))}</span></a>')


def _entry_page(e: dict, related: list[dict], zones: dict[str, str]) -> str:
    root = "../../"
    slug_cat, cat_name = CATS.get(e.get("categoria"), CATS["otro"])
    url = f"{config.SITE_URL}/d/{e['slug']}/"
    title = f"{e.get('titulo', '')} | GTA 6"
    desc = e.get("resumen", "")[:300]
    thumb = _thumb(e)

    if e.get("video_id"):
        media = (f'<button class="media" data-yt="{escape(e["video_id"])}" aria-label="Reproducir video">'
                 f'<img src="{escape(thumb)}" alt="{escape(e.get("titulo", ""))}"><span class="play"></span></button>')
    elif thumb:
        media = f'<a class="media" href="{escape(e["url"])}" rel="noopener"><img src="{escape(thumb)}" alt=""></a>'
    else:
        media = ""

    color = CAT_COLOR.get(e.get("categoria"), CAT_COLOR["otro"])
    tags = [f'<a class="tag cat" style="--c:{color}" href="{root}c/{slug_cat}/">{escape(cat_name)}</a>']
    if e.get("macro") in zones:
        place = e["region"] if e.get("region") and e["region"] != e["macro"] else ""
        tags.append(f'<a class="tag" href="{root}z/{zones[e["macro"]]}/">{escape(e["macro"])}'
                    + (f' · {escape(place)}' if place else "") + '</a>')
    elif e.get("region"):
        tags.append(f'<span class="tag">{escape(e["region"])}</span>')
    elif e.get("zona"):
        tags.append(f'<span class="tag">{escape(e["zona"])}</span>')
    if e.get("confianza") == "media":
        tags.append('<span class="tag warn">Sin confirmar</span>')
    if e.get("confirmado_por_comunidad"):
        tags.append('<span class="tag ok">Confirmado por la comunidad</span>')

    if e.get("pasos"):
        how = "<h2>Cómo hacerlo</h2><ol class=\"steps\">" + "".join(f"<li>{escape(p)}</li>" for p in e["pasos"]) + "</ol>"
    elif e.get("como_conseguirlo"):
        how = f'<h2>Cómo hacerlo</h2><p>{escape(e["como_conseguirlo"])}</p>'
    else:
        how = ""
    paragraphs = re.split(r"\n\s*\n", e.get("detalle") or "")
    detail = "".join(f"<p>{escape(par.strip())}</p>" for par in paragraphs if par.strip())
    detail = f"<h2>Qué es</h2>{detail}" if detail else ""
    zona = (f'<h2>Dónde está</h2><p>{escape(e["zona"])}</p>' if e.get("zona") else "")
    src_word = "vistas" if e.get("source") == "youtube" else "votos"
    sources = [f'<li><a href="{escape(e["url"])}" rel="noopener">{escape(e.get("author", ""))}</a> · '
               f'{_num(e.get("popularity"))} {src_word} · {_date(e.get("published_at", ""))}</li>']
    for s in e.get("fuentes_extra", []):
        if str(s.get("url", "")).startswith("http"):
            sources.append(f'<li><a href="{escape(s["url"])}" rel="noopener">{escape(s.get("author", ""))}</a></li>')
    spoiler_btn = ('<button class="spoiler-btn">Contiene spoilers · tocá para ver</button>'
                   if e.get("spoiler") else "")
    rel = ("<h2>Más " + escape(cat_name.lower()) + '</h2><div class="minis">'
           + "".join(_mini_card(r, root) for r in related) + "</div>") if related else ""

    body = f"""<nav class="crumbs"><a href="{root}">Inicio</a> › <a href="{root}c/{slug_cat}/">{escape(cat_name)}</a></nav>
<article class="entry">
  <div class="tags">{"".join(tags)}<button class="done-btn" type="button" data-slug="{escape(e['slug'])}" aria-pressed="false">Marcar como hecho</button></div>
  {spoiler_btn}
  <div class="{"spoiler" if e.get("spoiler") else ""}">
    <h1>{escape(e.get("titulo", ""))}</h1>
    {media}
    <p class="lead">{escape(e.get("resumen", ""))}</p>
    {detail}{zona}{how}
  </div>
  {tg_cta()}
  {_community(e, root)}
  <h2>Fuentes</h2><ul class="sources">{"".join(sources)}</ul>
  <p class="note">Resumen hecho automáticamente a partir del video original. Si algo no coincide con tu partida, mirá el video.</p>
</article>
{rel}"""

    jsonld = [{
        "@context": "https://schema.org", "@type": "BreadcrumbList",
        "itemListElement": [
            {"@type": "ListItem", "position": 1, "name": "Inicio", "item": f"{config.SITE_URL}/"},
            {"@type": "ListItem", "position": 2, "name": cat_name, "item": f"{config.SITE_URL}/c/{slug_cat}/"},
            {"@type": "ListItem", "position": 3, "name": e.get("titulo", ""), "item": url},
        ],
    }]
    if e.get("video_id"):
        jsonld.append({
            "@context": "https://schema.org", "@type": "VideoObject",
            "name": e.get("titulo", ""), "description": desc or e.get("titulo", ""),
            "thumbnailUrl": [thumb], "uploadDate": e.get("published_at", ""),
            "embedUrl": f"https://www.youtube.com/embed/{e['video_id']}",
            "contentUrl": e.get("url", ""),
        })
    return _layout(title=title, description=desc, canonical=url, root=root, body=body,
                   image=thumb, jsonld=jsonld, noindex=not indexable(e),
                   alternates=([("es", url), ("pt-BR", f"{config.SITE_URL}/pt/d/{e['slug']}/")]
                               if (e.get("pt") or {}).get("titulo") else None))


# Cada categoría responde a una búsqueda concreta de Google (título y H1 pensados para eso).
CAT_SEO = {
    "dinero": ("Cómo ganar dinero rápido en GTA 6",
               "Los métodos para hacer plata en GTA 6 que encontró la comunidad, ordenados por los más vistos. "
               "Cada uno tiene su guía con los pasos y el video original."),
    "vehiculo": ("Autos secretos y raros de GTA 6: dónde encontrarlos",
                 "Dónde aparecen los autos, motos y vehículos raros de GTA 6 y cómo conseguirlos, "
                 "con la ubicación y el video de quien los encontró."),
    "easter_egg": ("Easter eggs de GTA 6: todos los secretos encontrados",
                   "Referencias escondidas, guiños a otros juegos y secretos de GTA 6 que descubrió la comunidad."),
    "ubicacion_secreta": ("Lugares secretos de GTA 6 y cómo llegar",
                          "Habitaciones ocultas, zonas difíciles de encontrar y lugares secretos del mapa de GTA 6, "
                          "con cómo llegar a cada uno."),
    "arma": ("Armas secretas de GTA 6 y dónde conseguirlas",
             "Armas especiales, ubicaciones de armas y cómo conseguirlas en GTA 6."),
    "mision": ("Misiones secretas de GTA 6",
               "Misiones ocultas, golpes y cómo sacarles el máximo provecho en GTA 6."),
    "coleccionable": ("Coleccionables de GTA 6: ubicaciones y recompensas",
                      "Dónde encontrar los coleccionables de GTA 6 y qué se gana al juntarlos."),
    "mecanica_truco": ("Trucos y consejos de GTA 6",
                       "Trucos, controles ocultos y mecánicas poco conocidas de GTA 6 que encontró la comunidad. "
                       "Si aparecen códigos de trucos, se suman acá automáticamente."),
    "otro": ("Otros descubrimientos de GTA 6", "Otros descubrimientos de la comunidad en GTA 6."),
}


def _category_page(cat: str, entries: list[dict]) -> str:
    root = "../../"
    slug_cat, name = CATS[cat]
    url = f"{config.SITE_URL}/c/{slug_cat}/"
    h1, intro = CAT_SEO.get(cat, (f"{name} de GTA 6", CAT_INTRO[cat]))
    ranked = sorted(entries, key=lambda e: -int(e.get("popularity") or 0))
    top = [e for e in ranked if not e.get("spoiler")][:5]
    top_slugs = {e["slug"] for e in top}
    items = []
    for i, e in enumerate(top, 1):
        steps = "".join(f"<li>{escape(p)}</li>" for p in (e.get("pasos") or [])[:3])
        more = (f'<ol class="steps mini-steps">{steps}</ol>' if steps else "")
        items.append(f'<li><h3><span>{i:02d}</span><a href="{root}d/{e["slug"]}/">{escape(e.get("titulo", ""))}</a></h3>'
                     f'<p>{escape(e.get("resumen", ""))}</p>{more}'
                     f'<a class="more-link" href="{root}d/{e["slug"]}/">Ver la guía completa →</a></li>')
    rest = [e for e in ranked if e["slug"] not in top_slugs]
    nav = " · ".join(f'<a href="{root}c/{s}/">{escape(n)}</a>' for k, (s, n) in CATS.items() if k != cat)
    body = f"""<nav class="crumbs"><a href="{root}">Inicio</a> › {escape(name)}</nav>
<header class="page-head"><h1>{escape(h1)}</h1>
<p class="lead">{escape(intro)}</p>
<p class="note">{len(entries)} descubrimientos · se actualiza varias veces por día.</p></header>
{'<h2>Los más vistos</h2><ol class="top-guides">' + "".join(items) + "</ol>" if items else ""}
{f'<h2>Todos ({len(rest)} más)</h2><div class="minis">' + "".join(_mini_card(e, root) for e in rest) + "</div>" if rest else ""}
<p class="other">Otras categorías: {nav}</p>"""
    jsonld = [{
        "@context": "https://schema.org", "@type": "ItemList", "name": h1,
        "itemListElement": [{"@type": "ListItem", "position": i, "url": f"{config.SITE_URL}/d/{e['slug']}/",
                             "name": e.get("titulo", "")} for i, e in enumerate(ranked[:20], 1)],
    }]
    return _layout(title=f"{h1} | {config.SITE_NAME}", description=intro,
                   canonical=url, root=root, body=body, jsonld=jsonld)


def _zone_page(region: str, slug: str, entries: list[dict], zones: dict[str, str]) -> str:
    root = "../../"
    url = f"{config.SITE_URL}/z/{slug}/"
    intro = (f"Todos los secretos, easter eggs, autos, armas y lugares ocultos de GTA 6 que la "
             f"comunidad encontró en {region}.")
    others = " · ".join(f'<a href="{root}z/{s}/">{escape(r)}</a>' for r, s in zones.items() if r != region)
    body = f"""<nav class="crumbs"><a href="{root}">Inicio</a> › Zonas › {escape(region)}</nav>
<h1>Secretos en {escape(region)}</h1>
<p class="lead">{escape(intro)} {len(entries)} descubrimientos en esta zona, actualizados varias veces por día.</p>
<div class="minis">{"".join(_mini_card(e, root) for e in entries)}</div>
<p class="other">Otras zonas: {others or "pronto vas a ver más zonas acá."}</p>"""
    return _layout(title=f"Secretos en {region} | GTA 6 | {config.SITE_NAME}", description=intro,
                   canonical=url, root=root, body=body)


def _map_page(by_zone: dict[str, list[dict]], zones: dict[str, str]) -> str:
    root = "../"
    url = f"{config.SITE_URL}/mapa/"
    counts = {a: len(v) for a, v in by_zone.items()}
    links = {a: f"z/{s}/" for a, s in zones.items()}
    intro = ("Explorá los secretos de GTA 6 por zona. Tocá un área para ver todo lo que la "
             "comunidad encontró ahí.")
    cards = []
    for area, (_, _, color, desc) in AREAS.items():
        items = by_zone.get(area, [])
        top = "".join(f'<li><a href="{root}d/{e["slug"]}/">{escape(e.get("titulo", ""))}</a></li>'
                      for e in sorted(items, key=lambda e: -(e.get("popularity") or 0))[:4])
        head = (f'<a href="{root}z/{zones[area]}/">{escape(area)}</a>' if area in zones else escape(area))
        cards.append(f'<article class="area-card" style="--c:{color}"><h3>{head} <small>{len(items)}</small></h3>'
                     f'<p>{escape(desc)}</p>' + (f'<ul>{top}</ul>' if top else '<p class="note">Todavía sin secretos acá.</p>')
                     + '</article>')
    body = f"""<nav class="crumbs"><a href="{root}">Inicio</a> › Mapa</nav>
<h1>El mapa de los secretos</h1>
<p class="lead">{escape(intro)}</p>
<div class="map-wrap" data-reveal><div class="ex-map">{map_svg(counts, links, root)}<div class="radar" aria-hidden="true"></div></div></div>
<p class="note">Mapa esquemático hecho por WastedMap: no es el mapa oficial del juego y las ubicaciones son aproximadas. Cada burbuja agrupa los descubrimientos de esa zona.</p>
<div class="area-grid">{"".join(cards)}</div>"""
    return _layout(title=f"Mapa de secretos de GTA 6 por zona | {config.SITE_NAME}", description=intro,
                   canonical=url, root=root, body=body)


def _week_page(entries: list[dict]) -> str:
    root = "../"
    url = f"{config.SITE_URL}/semana/"
    intro = ("Los descubrimientos de GTA 6 que más se vieron en los últimos 7 días, "
             "ordenados por las vistas de los videos originales. Se actualiza varias veces por día.")
    ranking = home.rank_list(entries, root, summary=True) or '<p class="empty">Todavía no hay descubrimientos esta semana.</p>'
    body = f"""<nav class="crumbs"><a href="{root}">Inicio</a> › Top de la semana</nav>
<header class="page-head"><h1>Lo mejor de la semana en GTA 6</h1>
<p class="lead">{escape(intro)}</p></header>
{ranking}
{tg_cta("Recibí los hallazgos nuevos en Telegram o Bluesky")}"""
    return _layout(title=f"Lo mejor de la semana en GTA 6 | {config.SITE_NAME}", description=intro,
                   canonical=url, root=root, body=body)


def _top_week(entries: list[dict]) -> list[dict]:
    from datetime import datetime, timedelta, timezone

    since = (datetime.now(timezone.utc) - timedelta(days=WEEK_DAYS)).strftime("%Y-%m-%dT%H:%M:%SZ")
    recent = [e for e in entries if e.get("published_at", "") >= since and indexable(e)]
    return sorted(recent, key=lambda e: e.get("popularity") or 0, reverse=True)[:15]


CONTACT_EMAIL = "contacto@wastedmap.com"
_MAIL = f'<a href="mailto:{CONTACT_EMAIL}">{CONTACT_EMAIL}</a>'

STATIC_PAGES = {
    "acerca": ("Acerca de WastedMap",
               "Qué es WastedMap, cómo se arma y quién está detrás. Guía no oficial de GTA 6.",
               f"""<h1>Acerca de WastedMap</h1>
<p class="lead">WastedMap junta en un solo lugar los secretos, easter eggs, lugares ocultos y guías de GTA 6 que descubre la comunidad.</p>
<h2>Cómo funciona</h2>
<p>Varias veces por día revisamos los videos más vistos y recientes sobre descubrimientos del juego. Cada uno se clasifica por categoría y se resume en español con ayuda de inteligencia artificial. Los que no aportan un hallazgo concreto (noticias, opiniones, memes) se descartan, y cuando varios creadores muestran lo mismo, los juntamos en una sola página.</p>
<p>Los resúmenes son automáticos y pueden tener errores. Por eso cada página enlaza el video original: si algo no coincide con tu partida, el video es la referencia. Las páginas marcadas como "Sin confirmar" son hallazgos que todavía no están del todo claros.</p>
<h2>Los creadores</h2>
<p>Los videos pertenecen a sus autores y se muestran con el reproductor oficial de YouTube, así que las reproducciones cuentan para su canal. Siempre citamos al autor y enlazamos el original. Si sos creador y preferís que tu video no aparezca, escribinos a {_MAIL} y lo retiramos.</p>
<h2>Aviso legal</h2>
<p>WastedMap es una guía no oficial hecha por fans. No tiene relación con Rockstar Games ni con Take-Two Interactive, ni cuenta con su respaldo. Grand Theft Auto y GTA son marcas de Take-Two Interactive; se mencionan solo para indicar de qué juego habla el contenido.</p>
<p>Para consultas, correcciones o pedidos de retiro: {_MAIL}.</p>"""),
    "privacidad": ("Política de privacidad",
                   "Qué datos se recopilan al visitar WastedMap y cómo se usan.",
                   f"""<h1>Política de privacidad</h1>
<p class="note">Última actualización: 24 de noviembre de 2026.</p>
<p class="lead">WastedMap no tiene cuentas de usuario. Solo te pedimos un dato si decidís comentar, y nunca lo mostramos.</p>
<h2>Comentarios</h2>
<p>Para comentar te pedimos un nombre o apodo y un mail. El nombre y el comentario se publican en la guía. <b>El mail no se publica ni se guarda</b>: lo convertimos en una huella cifrada (hash) que no permite recuperarlo y que solo sirve para frenar el spam.</p>
<p>Cada comentario pasa por una revisión automática hecha con inteligencia artificial (Claude, de Anthropic), que recibe el nombre y el texto, nunca el mail, para decidir si cumple las reglas del sitio. Para comprobar que no sos un robot usamos Cloudflare Turnstile, que se carga recién cuando vas a escribir un comentario.</p>
<h2>Votos y "Me funcionó"</h2>
<p>Para que cada persona vote una sola vez por guía guardamos una huella anónima calculada a partir de tu conexión y tu navegador. No guardamos tu dirección IP ni ningún dato que te identifique.</p>
<p>Si querés que borremos un comentario tuyo, escribinos a {_MAIL} con el enlace de la guía y el nombre que usaste.</p>
<h2>Mi lista y "Marcar como hecho"</h2>
<p>Los secretos que marcás como hechos se guardan solo en tu navegador (almacenamiento local). No se mandan a ningún servidor y los podés borrar cuando quieras desde la página Mi lista.</p>
<h2>Estadísticas de visitas</h2>
<p>Usamos Cloudflare Web Analytics para saber cuántas personas visitan el sitio y qué páginas leen. Esta herramienta no usa cookies, no guarda tu dirección IP y no te sigue entre sitios: solo recibimos números agregados (visitas, páginas, país, tipo de dispositivo).</p>
<h2>Alojamiento</h2>
<p>El sitio está alojado en Cloudflare. Como cualquier servidor web, Cloudflare procesa datos técnicos de cada conexión (como la dirección IP) para entregar las páginas y proteger el sitio de ataques. Podés leer su política en <a href="https://www.cloudflare.com/privacypolicy/" rel="noopener">cloudflare.com/privacypolicy</a>.</p>
<h2>Videos de YouTube</h2>
<p>Los videos se cargan con el modo de privacidad mejorada de YouTube (youtube-nocookie.com) y recién cuando tocás el botón de reproducir. Hasta ese momento solo se muestra la imagen de portada, que se descarga de los servidores de YouTube sin cookies. Al reproducir un video, YouTube (Google) puede guardar cookies según su <a href="https://policies.google.com/privacy" rel="noopener">política de privacidad</a>.</p>
<h2>Enlaces externos</h2>
<p>Las páginas enlazan a los videos y publicaciones originales en otros sitios. Al entrar a esos sitios, se aplican sus propias políticas de privacidad.</p>
<h2>Publicidad y enlaces de afiliados</h2>
<p>Por ahora el sitio no muestra publicidad. Si en el futuro sumamos anuncios o enlaces de afiliados, vamos a actualizar esta página antes, explicar qué cookies usan y, cuando corresponda, pedirte el consentimiento.</p>
<h2>Tus derechos</h2>
<p>Podés pedirnos que borremos tus comentarios o consultar qué guardamos escribiendo a {_MAIL}. Como del mail solo guardamos una huella cifrada, no podemos usarlo para contactarte ni compartirlo con nadie.</p>"""),
    "contacto": ("Contacto",
                 "Cómo comunicarte con WastedMap: correcciones, sugerencias y pedidos de retiro de contenido.",
                 f"""<h1>Contacto</h1>
<p class="lead">Escribinos a {_MAIL}.</p>
<h2>Te respondemos por</h2>
<ul class="sources">
<li><b>Correcciones:</b> si un resumen tiene un error o un hallazgo no funciona como dice, contanos en qué página y qué viste.</li>
<li><b>Creadores:</b> si querés que retiremos tu video o que corrijamos cómo te citamos, mandanos el enlace y lo resolvemos en 72 horas como máximo.</li>
<li><b>Sugerencias:</b> descubrimientos que nos faltan, ideas para el sitio o cualquier otra cosa.</li>
</ul>
<p class="note">WastedMap es una guía no oficial: no podemos ayudar con problemas de cuenta, compras o soporte técnico del juego.</p>"""),
}


def _write_404() -> None:
    """Página de error propia: sin ella Cloudflare Pages devuelve la portada para cualquier
    dirección inexistente, y Google lo toma como contenido duplicado."""
    body = """<h1>Acá no hay nada… todavía</h1>
<p class="lead">Esta página no existe o el descubrimiento se juntó con otro igual.</p>
<p><a class="btn primary" href="/">Ir al inicio</a> <a class="btn" href="/mapa/">Abrir el mapa</a></p>"""
    page = _layout(title=f"Página no encontrada | {config.SITE_NAME}", description="Página no encontrada.",
                   canonical=f"{config.SITE_URL}/", root="/", body=body, noindex=True)
    (config.DOCS_DIR / "404.html").write_text(page, encoding="utf-8")


def _write_static_pages() -> None:
    for slug, (title, desc, body) in STATIC_PAGES.items():
        root = "../"
        page = _layout(title=f"{title} | {config.SITE_NAME}", description=desc,
                       canonical=f"{config.SITE_URL}/{slug}/", root=root,
                       body=f'<nav class="crumbs"><a href="{root}">Inicio</a> › {escape(title)}</nav>\n{body}')
        out = config.DOCS_DIR / slug / "index.html"
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(page, encoding="utf-8")


def build(entries: list[dict]) -> None:
    """Regenera todas las páginas a partir de las entradas (y agrega 'slug' a cada una)."""
    docs = config.DOCS_DIR
    for e in entries:
        e["slug"] = slug_for(e)

    by_cat: dict[str, list[dict]] = {}
    for e in entries:
        by_cat.setdefault(e.get("categoria") if e.get("categoria") in CATS else "otro", []).append(e)

    by_zone: dict[str, list[dict]] = {}
    for e in entries:
        if e.get("macro") in AREAS:
            by_zone.setdefault(e["macro"], []).append(e)
    by_zone = {r: v for r, v in sorted(by_zone.items(), key=lambda kv: -len(kv[1]))
               if len(v) >= MIN_ZONE_ENTRIES}
    zones = {r: _slugify(r, "zona") for r in by_zone}
    week = _top_week(entries)

    _write_static_pages()
    _write_404()

    # Se regeneran desde cero: así desaparecen las que ya no están (duplicados juntados, etc.).
    for folder in ("d", "c", "z", "semana", "mapa", "descubrimientos", "lista"):
        shutil.rmtree(docs / folder, ignore_errors=True)

    for e in entries:
        cat = e.get("categoria") if e.get("categoria") in CATS else "otro"
        related = [r for r in by_cat[cat] if r is not e][:6]
        out = docs / "d" / e["slug"] / "index.html"
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(_entry_page(e, related, zones), encoding="utf-8")

    for cat, items in by_cat.items():
        out = docs / "c" / CATS[cat][0] / "index.html"
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(_category_page(cat, items), encoding="utf-8")

    for region, items in by_zone.items():
        out = docs / "z" / zones[region] / "index.html"
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(_zone_page(region, zones[region], items, zones), encoding="utf-8")

    out = docs / "mapa" / "index.html"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(_map_page(by_zone, zones), encoding="utf-8")

    out = docs / "semana" / "index.html"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(_week_page(week), encoding="utf-8")

    from datetime import datetime, timezone
    updated = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    (docs / "index.html").write_text(_layout(
        title=f"{config.SITE_NAME} · Secretos, easter eggs y mapa de GTA 6",
        description=("Secretos, easter eggs, lugares ocultos y guías de GTA 6 que encuentra la comunidad, "
                     "ordenados en un mapa de Leonida y actualizados varias veces por día. Guía no oficial."),
        canonical=f"{config.SITE_URL}/", root="", og_type="website", bare=True,
        body=home.home_body(entries, by_cat, by_zone, zones, week, updated)), encoding="utf-8")

    out = docs / "lista" / "index.html"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(_layout(
        title=f"Mi lista de secretos de GTA 6 | {config.SITE_NAME}",
        description="Tildá los secretos de GTA 6 que ya encontraste y mirá cuánto te falta, por categoría. Sin registrarte.",
        canonical=f"{config.SITE_URL}/lista/", root="../", wide=False,
        body=home.checklist_body(entries, by_cat, "../")), encoding="utf-8")

    out = docs / "descubrimientos" / "index.html"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(_layout(
        title=f"Todos los descubrimientos de GTA 6 | {config.SITE_NAME}",
        description=("Todos los secretos, easter eggs, autos, armas y guías de GTA 6 que reunió WastedMap, "
                     "con buscador y filtro por categoría."),
        canonical=f"{config.SITE_URL}/descubrimientos/", root="../", wide=True,
        body=home.discover_body(entries, by_cat, "../", _ver("discover.js"))), encoding="utf-8")

    urls = [(f"{config.SITE_URL}/", entries[0]["published_at"] if entries else "")]
    urls += [(f"{config.SITE_URL}/c/{CATS[k][0]}/", v[0].get("published_at", "")) for k, v in by_cat.items()]
    urls += [(f"{config.SITE_URL}/z/{zones[r]}/", v[0].get("published_at", "")) for r, v in by_zone.items()]
    urls.append((f"{config.SITE_URL}/mapa/", entries[0]["published_at"] if entries else ""))
    urls.append((f"{config.SITE_URL}/descubrimientos/", entries[0]["published_at"] if entries else ""))
    urls.append((f"{config.SITE_URL}/lista/", ""))
    urls.append((f"{config.SITE_URL}/semana/", week[0].get("published_at", "") if week else ""))
    # Las dudosas no van al sitemap (y llevan noindex): solo indexamos lo confirmado.
    urls += [(f"{config.SITE_URL}/d/{e['slug']}/", e.get("published_at", "")) for e in entries if indexable(e)]
    urls += [(f"{config.SITE_URL}/{slug}/", "") for slug in STATIC_PAGES]
    import sys
    from . import pt
    urls += pt.build(entries, sys.modules[__name__])
    sitemap = "".join(f"<url><loc>{escape(u)}</loc>" + (f"<lastmod>{d[:10]}</lastmod>" if d else "") + "</url>"
                      for u, d in urls)
    (docs / "sitemap.xml").write_text(
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        f'<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">{sitemap}</urlset>\n',
        encoding="utf-8")
    (docs / "robots.txt").write_text(
        f"User-agent: *\nAllow: /\nSitemap: {config.SITE_URL}/sitemap.xml\n", encoding="utf-8")
    n_index = sum(1 for e in entries if indexable(e))
    print(f"[web] {len(entries)} páginas de descubrimientos ({n_index} indexables), "
          f"{len(by_cat)} de categorías, {len(by_zone)} de zonas")
