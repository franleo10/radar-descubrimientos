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
from .mapa import AREAS, map_svg

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
CAT_COLOR = {
    "easter_egg": "#ff3d8b", "ubicacion_secreta": "#2ee6d6", "coleccionable": "#ffd54a",
    "vehiculo": "#ff8a3d", "arma": "#ff4d4d", "dinero": "#4ade80", "mision": "#a78bfa",
    "mecanica_truco": "#60a5fa", "otro": "#958ba9",
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


def _slugify(text: str, fallback: str = "descubrimiento") -> str:
    text = unicodedata.normalize("NFKD", text or "")
    text = re.sub(r"[^a-z0-9]+", "-", text.encode("ascii", "ignore").decode().lower()).strip("-")
    return text[:60].rstrip("-") or fallback


def slug_for(e: dict) -> str:
    return f"{_slugify(e.get('titulo'))}-{hashlib.sha1(e['id'].encode()).hexdigest()[:5]}"


def indexable(e: dict) -> bool:
    """Solo las confirmadas van a Google; las dudosas se ven en la web pero no se indexan."""
    return e.get("confianza") == "alta"


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


def _css_version() -> str:
    """Huella del CSS: cambia cuando cambia el archivo, así nadie ve estilos viejos en caché."""
    css = config.DOCS_DIR / "site.css"
    return hashlib.sha1(css.read_bytes()).hexdigest()[:8] if css.exists() else "0"


def _layout(*, title: str, description: str, canonical: str, root: str, body: str,
            image: str = "", jsonld: list | None = None, noindex: bool = False) -> str:
    robots = '<meta name="robots" content="noindex, follow">' if noindex else ""
    # Sin imagen propia (inicio, categorías, zonas...) se usa la de la marca.
    og_image = f'<meta property="og:image" content="{escape(image or config.SITE_URL + "/og.png")}">'
    ld = "".join(f'<script type="application/ld+json">{_safe_json(x)}</script>' for x in (jsonld or []))
    return f"""<!doctype html>
<html lang="es">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{escape(title)}</title>
<meta name="description" content="{escape(description)}">
<link rel="canonical" href="{escape(canonical)}">
{robots}
<meta property="og:type" content="article">
<meta property="og:title" content="{escape(title)}">
<meta property="og:description" content="{escape(description)}">
<meta property="og:url" content="{escape(canonical)}">
{og_image}
<meta name="twitter:card" content="summary_large_image">
<link rel="icon" href="{root}favicon.svg" type="image/svg+xml">
<link rel="icon" href="{root}favicon-32.png" sizes="32x32" type="image/png">
<link rel="apple-touch-icon" href="{root}apple-touch-icon.png">
<meta name="theme-color" content="#0d0b14">
<link rel="preload" href="{root}fonts/anton.woff2" as="font" type="font/woff2" crossorigin>
<link rel="stylesheet" href="{root}site.css?v={_css_version()}">
{ld}
</head>
<body>
<header class="topbar"><div class="wrap">{logo(root, "lg")}
<nav class="nav"><a class="hide-sm" href="{root}mapa/">Mapa</a>{tg_link()}{bsky_link()}<a class="pill" href="{root}semana/">🔥 Top de la semana</a></nav></div></header>
<main class="page"><div class="wrap">
{body}
</div></main>
<footer class="foot"><div class="wrap">
<div>{logo(root, "lg2")}
<p>Guía no oficial hecha por fans. No tiene relación con Rockstar Games ni Take-Two Interactive. Los videos son de sus autores y se muestran con el reproductor original.</p></div>
<nav><a href="{root}semana/">Top de la semana</a>{tg_link("tg", "Telegram")}{bsky_link()}<a href="{root}acerca/">Acerca de</a><a href="{root}privacidad/">Privacidad</a><a href="{root}contacto/">Contacto</a></nav>
</div></footer>
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
        tags.append(f'<a class="tag" href="{root}z/{zones[e["macro"]]}/">📍 {escape(e["macro"])}'
                    + (f' · {escape(place)}' if place else "") + '</a>')
    elif e.get("region"):
        tags.append(f'<span class="tag">📍 {escape(e["region"])}</span>')
    elif e.get("zona"):
        tags.append(f'<span class="tag">📍 {escape(e["zona"])}</span>')
    if e.get("confianza") == "media":
        tags.append('<span class="tag warn">Sin confirmar</span>')

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
  <div class="tags">{"".join(tags)}</div>
  {spoiler_btn}
  <div class="{"spoiler" if e.get("spoiler") else ""}">
    <h1>{escape(e.get("titulo", ""))}</h1>
    {media}
    <p class="lead">{escape(e.get("resumen", ""))}</p>
    {detail}{zona}{how}
  </div>
  {tg_cta()}
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
                   image=thumb, jsonld=jsonld, noindex=not indexable(e))


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
<div class="map-wrap">{map_svg(counts, links, root)}</div>
<p class="note">Mapa esquemático hecho por WastedMap: no es el mapa oficial del juego y las ubicaciones son aproximadas. Cada burbuja agrupa los descubrimientos de esa zona.</p>
<div class="area-grid">{"".join(cards)}</div>"""
    return _layout(title=f"Mapa de secretos de GTA 6 por zona | {config.SITE_NAME}", description=intro,
                   canonical=url, root=root, body=body)


def _week_page(entries: list[dict]) -> str:
    root = "../"
    url = f"{config.SITE_URL}/semana/"
    intro = ("Los descubrimientos de GTA 6 que más se vieron en los últimos 7 días, "
             "ordenados por popularidad. Se actualiza solo varias veces por día.")
    items = "".join(
        f'<li><a href="{root}d/{e["slug"]}/">{escape(e.get("titulo", ""))}</a>'
        f'<span class="note"> · {escape(CATS.get(e.get("categoria"), CATS["otro"])[1])}'
        f' · {_num(e.get("popularity"))} vistas</span><br>{escape(e.get("resumen", ""))}</li>'
        for e in entries)
    body = f"""<nav class="crumbs"><a href="{root}">Inicio</a> › Lo mejor de la semana</nav>
<h1>Lo mejor de la semana en GTA 6</h1>
<p class="lead">{escape(intro)}</p>
<ol class="ranking">{items or "<li>Todavía no hay descubrimientos esta semana.</li>"}</ol>
{tg_cta("Recibí el top de cada semana en Telegram")}"""
    return _layout(title=f"Lo mejor de la semana en GTA 6 | {config.SITE_NAME}", description=intro,
                   canonical=url, root=root, body=body)


def _top_week(entries: list[dict]) -> list[dict]:
    from datetime import datetime, timedelta, timezone

    since = (datetime.now(timezone.utc) - timedelta(days=WEEK_DAYS)).strftime("%Y-%m-%dT%H:%M:%SZ")
    recent = [e for e in entries if e.get("published_at", "") >= since and indexable(e)]
    return sorted(recent, key=lambda e: e.get("popularity") or 0, reverse=True)[:15]


def _home_static(entries: list[dict], counts: dict[str, int], zones: dict[str, str]) -> str:
    cats = " · ".join(f'<a href="c/{CATS[k][0]}/">{escape(CATS[k][1])} ({n})</a>'
                      for k, n in counts.items())
    zl = " · ".join(f'<a href="z/{s}/">{escape(r)}</a>' for r, s in zones.items())
    items = "".join(f'<li><a href="d/{e["slug"]}/">{escape(e.get("titulo", ""))}</a></li>' for e in entries)
    return (f'<p><a href="semana/">Lo mejor de la semana</a></p><p>{cats}</p>'
            + (f"<p>Zonas: {zl}</p>" if zl else "") + f'<ul class="static-list">{items}</ul>')


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
<p class="note">Última actualización: 23 de noviembre de 2026.</p>
<p class="lead">WastedMap no tiene cuentas de usuario ni formularios: no te pedimos ningún dato personal para usar el sitio.</p>
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
<p>Como no guardamos datos personales tuyos, no hay información para consultar ni borrar. Igual, si tenés cualquier pregunta sobre privacidad, escribinos a {_MAIL}.</p>"""),
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

    # Se regeneran desde cero: así desaparecen las que ya no están (duplicados juntados, etc.).
    for folder in ("d", "c", "z", "semana", "mapa"):
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

    index = docs / "index.html"
    html = index.read_text(encoding="utf-8")
    counts = {k: len(by_cat[k]) for k in CATS if k in by_cat}
    static = _home_static(entries, counts, zones)
    html = _MARK.sub(lambda m: m.group(1) + static + m.group(2), html)
    mini = map_svg({k: len(v) for k, v in by_zone.items()}, {}, "")
    html = re.sub(r"(<!--MAP-->).*?(<!--/MAP-->)", lambda m: m.group(1) + mini + m.group(2), html, flags=re.S)
    html = re.sub(r'href="site\.css(\?v=[^"]*)?"', f'href="site.css?v={_css_version()}"', html)
    html = re.sub(r'<link rel="canonical" href="[^"]*">',
                  f'<link rel="canonical" href="{escape(config.SITE_URL)}/">', html)
    index.write_text(html, encoding="utf-8")

    urls = [(f"{config.SITE_URL}/", entries[0]["published_at"] if entries else "")]
    urls += [(f"{config.SITE_URL}/c/{CATS[k][0]}/", v[0].get("published_at", "")) for k, v in by_cat.items()]
    urls += [(f"{config.SITE_URL}/z/{zones[r]}/", v[0].get("published_at", "")) for r, v in by_zone.items()]
    urls.append((f"{config.SITE_URL}/mapa/", entries[0]["published_at"] if entries else ""))
    urls.append((f"{config.SITE_URL}/semana/", week[0].get("published_at", "") if week else ""))
    # Las dudosas no van al sitemap (y llevan noindex): solo indexamos lo confirmado.
    urls += [(f"{config.SITE_URL}/d/{e['slug']}/", e.get("published_at", "")) for e in entries if indexable(e)]
    urls += [(f"{config.SITE_URL}/{slug}/", "") for slug in STATIC_PAGES]
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
