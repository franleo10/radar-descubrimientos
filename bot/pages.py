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

CATS = {
    "easter_egg": ("easter-eggs", "Easter eggs"),
    "ubicacion_secreta": ("lugares-secretos", "Lugares secretos"),
    "coleccionable": ("coleccionables", "Coleccionables"),
    "vehiculo": ("vehiculos", "Vehículos"),
    "arma": ("armas", "Armas"),
    "dinero": ("dinero", "Dinero"),
    "mision": ("misiones", "Misiones"),
    "mecanica_truco": ("mecanicas-y-tips", "Mecánicas y tips"),
    "otro": ("otros", "Otros"),
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
_MARK = re.compile(r"(<!--STATIC-->).*?(<!--/STATIC-->)", re.S)


def slug_for(e: dict) -> str:
    text = unicodedata.normalize("NFKD", e.get("titulo") or "descubrimiento")
    text = re.sub(r"[^a-z0-9]+", "-", text.encode("ascii", "ignore").decode().lower()).strip("-")
    text = text[:60].rstrip("-") or "descubrimiento"
    return f"{text}-{hashlib.sha1(e['id'].encode()).hexdigest()[:5]}"


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


def _layout(*, title: str, description: str, canonical: str, root: str, body: str,
            image: str = "", jsonld: list | None = None) -> str:
    og_image = f'<meta property="og:image" content="{escape(image)}">' if image else ""
    ld = "".join(f'<script type="application/ld+json">{_safe_json(x)}</script>' for x in (jsonld or []))
    return f"""<!doctype html>
<html lang="es">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{escape(title)}</title>
<meta name="description" content="{escape(description)}">
<link rel="canonical" href="{escape(canonical)}">
<meta property="og:type" content="article">
<meta property="og:title" content="{escape(title)}">
<meta property="og:description" content="{escape(description)}">
<meta property="og:url" content="{escape(canonical)}">
{og_image}
<meta name="twitter:card" content="summary_large_image">
<link rel="stylesheet" href="{root}page.css">
{ld}
</head>
<body>
<header><div class="wrap"><a class="brand" href="{root}">{escape(config.SITE_NAME)}</a></div></header>
<main><div class="wrap">
{body}
</div></main>
<footer>Guía no oficial hecha por fans. No tiene relación con Rockstar Games ni Take-Two Interactive.<br>
Los videos y publicaciones son de sus autores y se muestran con el reproductor o el enlace original.</footer>
<script>
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


def _entry_page(e: dict, related: list[dict]) -> str:
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

    tags = [f'<a class="tag cat" href="{root}c/{slug_cat}/">{escape(cat_name)}</a>']
    if e.get("zona"):
        tags.append(f'<span class="tag">📍 {escape(e["zona"])}</span>')
    if e.get("confianza") == "media":
        tags.append('<span class="tag warn">Sin confirmar</span>')

    how = (f'<h2>Cómo hacerlo</h2><p>{escape(e["como_conseguirlo"])}</p>' if e.get("como_conseguirlo") else "")
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
  <div class="tags">{"".join(tags)}</div>
  {spoiler_btn}
  <div class="{"spoiler" if e.get("spoiler") else ""}">
    <h1>{escape(e.get("titulo", ""))}</h1>
    {media}
    <p class="lead">{escape(e.get("resumen", ""))}</p>
    {zona}{how}
  </div>
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
                   image=thumb, jsonld=jsonld)


def _category_page(cat: str, entries: list[dict]) -> str:
    root = "../../"
    slug_cat, name = CATS[cat]
    url = f"{config.SITE_URL}/c/{slug_cat}/"
    intro = CAT_INTRO[cat]
    nav = " · ".join(f'<a href="{root}c/{s}/">{escape(n)}</a>' for k, (s, n) in CATS.items() if k != cat)
    body = f"""<nav class="crumbs"><a href="{root}">Inicio</a> › {escape(name)}</nav>
<h1>{escape(name)} de GTA 6</h1>
<p class="lead">{escape(intro)} {len(entries)} descubrimientos, actualizados varias veces por día.</p>
<div class="minis">{"".join(_mini_card(e, root) for e in entries)}</div>
<p class="other">Otras categorías: {nav}</p>"""
    return _layout(title=f"{name} de GTA 6 | {config.SITE_NAME}", description=intro,
                   canonical=url, root=root, body=body)


def _home_static(entries: list[dict], counts: dict[str, int]) -> str:
    cats = " · ".join(f'<a href="c/{CATS[k][0]}/">{escape(CATS[k][1])} ({n})</a>'
                      for k, n in counts.items())
    items = "".join(f'<li><a href="d/{e["slug"]}/">{escape(e.get("titulo", ""))}</a></li>' for e in entries)
    return f'<p>{cats}</p><ul class="static-list">{items}</ul>'


def build(entries: list[dict]) -> None:
    """Regenera todas las páginas a partir de las entradas (y agrega 'slug' a cada una)."""
    docs = config.DOCS_DIR
    for e in entries:
        e["slug"] = slug_for(e)

    by_cat: dict[str, list[dict]] = {}
    for e in entries:
        by_cat.setdefault(e.get("categoria") if e.get("categoria") in CATS else "otro", []).append(e)

    # Se regeneran desde cero: así desaparecen las que ya no están (duplicados juntados, etc.).
    for folder in ("d", "c"):
        shutil.rmtree(docs / folder, ignore_errors=True)

    for e in entries:
        cat = e.get("categoria") if e.get("categoria") in CATS else "otro"
        related = [r for r in by_cat[cat] if r is not e][:6]
        out = docs / "d" / e["slug"] / "index.html"
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(_entry_page(e, related), encoding="utf-8")

    for cat, items in by_cat.items():
        out = docs / "c" / CATS[cat][0] / "index.html"
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(_category_page(cat, items), encoding="utf-8")

    index = docs / "index.html"
    html = index.read_text(encoding="utf-8")
    counts = {k: len(by_cat[k]) for k in CATS if k in by_cat}
    static = _home_static(entries, counts)
    html = _MARK.sub(lambda m: m.group(1) + static + m.group(2), html)
    html = re.sub(r'<link rel="canonical" href="[^"]*">',
                  f'<link rel="canonical" href="{escape(config.SITE_URL)}/">', html)
    index.write_text(html, encoding="utf-8")

    urls = [(f"{config.SITE_URL}/", entries[0]["published_at"] if entries else "")]
    urls += [(f"{config.SITE_URL}/c/{CATS[k][0]}/", v[0].get("published_at", "")) for k, v in by_cat.items()]
    urls += [(f"{config.SITE_URL}/d/{e['slug']}/", e.get("published_at", "")) for e in entries]
    sitemap = "".join(f"<url><loc>{escape(u)}</loc>" + (f"<lastmod>{d[:10]}</lastmod>" if d else "") + "</url>"
                      for u, d in urls)
    (docs / "sitemap.xml").write_text(
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        f'<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">{sitemap}</urlset>\n',
        encoding="utf-8")
    (docs / "robots.txt").write_text(
        f"User-agent: *\nAllow: /\nSitemap: {config.SITE_URL}/sitemap.xml\n", encoding="utf-8")
    print(f"[web] {len(entries)} páginas de descubrimientos y {len(by_cat)} de categorías")
