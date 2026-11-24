"""Portada y página de descubrimientos, generadas con los datos reales del bot.

Todo lo que se muestra sale de las entradas: no hay números, usuarios ni textos inventados.
"""
from __future__ import annotations

from datetime import datetime, timezone
from html import escape

from .brand import BUTTERFLY, PLANE, bsky_link, tg_link
from .mapa import AREAS, map_svg


def _p():
    from . import pages  # import diferido: pages importa este módulo
    return pages


def ago(iso: str) -> str:
    """Fecha relativa: el texto se recalcula en el navegador (ver el script del layout)."""
    p = _p()
    return f'<time datetime="{escape(iso)}" data-ago>{p._date(iso)}</time>' if iso else ""


def cat_of(e: dict) -> tuple[str, str, str]:
    p = _p()
    k = e.get("categoria") if e.get("categoria") in p.CATS else "otro"
    slug, name = p.CATS[k]
    return slug, name, p.CAT_COLOR[k]


def meta(e: dict, root: str = "", zone: bool = True, when: bool = True) -> str:
    slug, name, color = cat_of(e)
    parts = [f'<a class="m-cat" style="--c:{color}" href="{root}c/{slug}/">{escape(name)}</a>']
    place = e.get("macro") or e.get("region")
    if zone and place:
        parts.append(f'<span>{escape(place)}</span>')
    if when and e.get("published_at"):
        parts.append(ago(e["published_at"]))
    return '<div class="meta">' + "".join(parts) + "</div>"


def views(e: dict) -> str:
    p = _p()
    word = "vistas" if e.get("source") == "youtube" else "votos"
    return f"{p._num(e.get('popularity')).replace('.', ',')} {word}"


def rank_list(entries: list[dict], root: str, limit: int | None = None, summary: bool = False) -> str:
    """Ranking con barra proporcional a las vistas reales."""
    items = entries[:limit] if limit else entries
    if not items:
        return ""
    top = max((e.get("popularity") or 0) for e in items) or 1
    rows = []
    for i, e in enumerate(items, 1):
        _, name, color = cat_of(e)
        pct = max(4, round(100 * (e.get("popularity") or 0) / top))
        sub = escape(name) + (f" · {escape(e['macro'])}" if e.get("macro") else "")
        desc = f'<span class="rs">{escape(e.get("resumen", ""))}</span>' if summary and e.get("resumen") else ""
        rows.append(
            f'<li style="--c:{color}"><a href="{root}d/{e["slug"]}/">'
            f'<span class="rk">{i:02d}</span>'
            f'<span class="rt"><b>{escape(e.get("titulo", ""))}</b><small>{sub}</small>{desc}</span>'
            f'<span class="rbar" aria-hidden="true"><i style="width:{pct}%"></i></span>'
            f'<span class="rv">{views(e)}</span></a></li>')
    return '<ol class="rank">' + "".join(rows) + "</ol>"


def card(e: dict, root: str) -> str:
    """Tarjeta del listado de descubrimientos (misma estructura que arma discover.js)."""
    p = _p()
    thumb = p._thumb(e)
    img = f'<img loading="lazy" src="{escape(thumb)}" alt="">' if thumb else ""
    flag = '<span class="flag">Sin confirmar</span>' if e.get("confianza") == "media" else ""
    spoiler = " is-spoiler" if e.get("spoiler") else ""
    return (f'<article class="card{spoiler}"><a class="thumb" href="{root}d/{e["slug"]}/" tabindex="-1" aria-hidden="true">{img}</a>'
            f'<div class="card-body">{meta(e, root, zone=True, when=False)}'
            f'<h3><a href="{root}d/{e["slug"]}/">{escape(e.get("titulo", ""))}</a></h3>'
            f'<p>{escape(e.get("resumen", ""))}</p>'
            f'<div class="card-foot"><span>{escape(e.get("author", ""))}</span>{ago(e.get("published_at", ""))}{flag}</div></div></article>')


# ---------------------------------------------------------------- portada

def _explorer(by_zone: dict[str, list[dict]], zones: dict[str, str]) -> str:
    counts = {a: len(v) for a, v in by_zone.items()}
    links = {a: f"z/{s}/" for a, s in zones.items()}
    order = sorted(AREAS, key=lambda a: -counts.get(a, 0))
    rows = []
    for area in order:
        _, _, color, desc = AREAS[area]
        n = counts.get(area, 0)
        if n:
            best = max(by_zone[area], key=lambda e: e.get("popularity") or 0)
            rows.append(
                f'<li><a href="{links[area]}" data-area="{escape(area)}" style="--c:{color}">'
                f'<span class="zn">{escape(area)}</span><span class="zc">{n}</span>'
                f'<span class="zd">{escape(desc)}</span>'
                f'<span class="zt">Más visto: {escape(best.get("titulo", ""))}</span></a></li>')
        else:
            rows.append(f'<li class="off"><span data-area="{escape(area)}" style="--c:{color}">'
                        f'<span class="zn">{escape(area)}</span><span class="zc">—</span>'
                        f'<span class="zd">{escape(desc)}. Todavía sin secretos.</span></span></li>')
    active = sum(1 for a in AREAS if counts.get(a))
    return f"""<div class="explorer" id="mapa">
  <div class="ex-bar">
    <p><b>Leonida</b><span>{active} de {len(AREAS)} zonas con secretos · ubicaciones aproximadas</span></p>
    <a class="btn on-dark" href="mapa/">Abrir el mapa completo <span aria-hidden="true">→</span></a>
  </div>
  <div class="ex-body">
    <div class="ex-map">{map_svg(counts, links, "", legend=False)}</div>
    <ol class="ex-zones">{"".join(rows)}</ol>
  </div>
</div>"""


def _recent(entries: list[dict], skip: set[str]) -> str:
    p = _p()
    pool = [e for e in sorted(entries, key=lambda e: e.get("published_at", ""), reverse=True)
            if not e.get("spoiler") and p._thumb(e) and e["slug"] not in skip]
    if not pool:
        return ""
    lead, rest = pool[0], pool[1:5]
    rows = "".join(
        f'<li><a class="r-row" href="d/{e["slug"]}/"><img loading="lazy" src="{escape(p._thumb(e))}" alt="">'
        f'<span><b>{escape(e.get("titulo", ""))}</b></span></a>{meta(e)}</li>' for e in rest)
    return f"""<section class="sec" id="recientes"><div class="wrap">
  <div class="sec-head">
    <div><p class="overline">Recién agregados</p><h2>Descubrimientos recientes</h2></div>
    <a class="more-link" href="descubrimientos/">Ver los {len(entries)} <span aria-hidden="true">→</span></a>
  </div>
  <div class="recent">
    <article class="r-lead">
      <a class="thumb" href="d/{lead["slug"]}/" tabindex="-1" aria-hidden="true"><img src="{escape(p._thumb(lead))}" alt=""></a>
      {meta(lead)}
      <h3><a href="d/{lead["slug"]}/">{escape(lead.get("titulo", ""))}</a></h3>
      <p>{escape(lead.get("resumen", ""))}</p>
    </article>
    <ol class="r-list">{rows}</ol>
  </div>
</div></section>"""


def _top(week: list[dict]) -> str:
    if len(week) < 3:
        return ""
    return f"""<section class="band band-pink" id="top"><div class="wrap">
  <div class="sec-head">
    <div><p class="overline">Top de la semana</p><h2>Lo que más se está mirando ahora</h2></div>
    <a class="more-link" href="semana/">Ver el top completo <span aria-hidden="true">→</span></a>
  </div>
  {rank_list(week, "", limit=5)}
  <p class="band-note">Ordenado por las vistas de los videos originales en los últimos 7 días.</p>
</div></section>"""


def _categories(by_cat: dict[str, list[dict]]) -> str:
    p = _p()
    rows = []
    for k, items in sorted(by_cat.items(), key=lambda kv: -len(kv[1])):
        slug, name = p.CATS[k]
        n = len(items)
        tier = "t1" if n >= 20 else "t2" if n >= 8 else "t3"
        ex = sorted(items, key=lambda e: -(e.get("popularity") or 0))[:2]
        sample = " · ".join(escape(e.get("titulo", "")) for e in ex)
        rows.append(f'<li class="{tier}" style="--c:{p.CAT_COLOR[k]}"><a href="c/{slug}/">'
                    f'<span class="cn">{escape(name)}</span><span class="cc">{n}</span>'
                    f'<span class="cx">{sample}</span><span class="arr" aria-hidden="true">→</span></a></li>')
    return f"""<section class="sec" id="categorias"><div class="wrap cat-layout">
  <div class="cat-intro">
    <p class="overline">Explorar</p>
    <h2>Por tipo de descubrimiento</h2>
    <p>Desde autos raros hasta formas de hacer plata al empezar. Cada categoría junta las guías con sus pasos y el video original.</p>
  </div>
  <ul class="cats">{"".join(rows)}</ul>
</div></section>"""


def _community(updated: str, n_community: int) -> str:
    confirmed = (f"<p><b>{n_community}</b> guía{'s' if n_community != 1 else ''} ya confirmada{'s' if n_community != 1 else ''} por la comunidad.</p>"
                 if n_community else "")
    return f"""<section class="band band-ink" id="comunidad"><div class="wrap com">
  <div class="com-copy">
    <p class="overline">Cómo se arma</p>
    <h2>Siempre hay algo nuevo para descubrir</h2>
    <p>Varias veces por día revisamos los videos nuevos de la gente que anda encontrando secretos en GTA 6. Los resumimos en español, los ordenamos por categoría y los ubicamos en el mapa.</p>
    {confirmed}
    <p class="com-updated">Última actualización: {ago(updated)}</p>
  </div>
  <ol class="how">
    <li><span class="hn">1</span><div><b>Encontramos</b><p>Videos nuevos de creadores que muestran un hallazgo concreto. Noticias, opiniones y memes quedan afuera.</p></div></li>
    <li><span class="hn">2</span><div><b>Resumimos</b><p>Qué es, dónde está y cómo hacerlo, con el video original y su autor citado.</p></div></li>
    <li><span class="hn">3</span><div><b>Confirmás vos</b><p>Si lo probaste, marcá "Me funcionó" en la guía. Cuando varias personas lo confirman, deja de figurar como "Sin confirmar".</p></div></li>
  </ol>
  <div class="follow"><span>Seguí los hallazgos nuevos</span>{tg_link("social")}{bsky_link("social")}</div>
</div></section>"""


def home_body(entries, by_cat, by_zone, zones, week, updated: str) -> str:
    n_conf = sum(1 for e in entries if e.get("confianza") == "alta")
    n_comm = sum(1 for e in entries if e.get("confirmado_por_comunidad"))
    top_slugs = {e["slug"] for e in week[:5]}
    return f"""<section class="hero"><div class="wrap">
  <div class="hero-top">
    <div class="hero-copy">
      <p class="overline"><span class="live" aria-hidden="true"></span>Guía no oficial · actualizada {ago(updated)}</p>
      <h1>Todos los secretos de GTA&nbsp;6 en <em>un solo mapa</em></h1>
    </div>
    <div class="hero-aside">
      <p class="lede">Easter eggs, lugares ocultos, autos raros y guías que descubre la comunidad, resumidos en español y con el video original.</p>
      <form class="search" action="descubrimientos/" role="search">
        <label class="sr" for="q">Buscar un secreto</label>
        <svg viewBox="0 0 24 24" aria-hidden="true"><circle cx="11" cy="11" r="7"/><path d="m20 20-3.5-3.5"/></svg>
        <input id="q" name="q" type="search" placeholder="Buscá un secreto: muelle, Cheetah, dinero…" autocomplete="off">
        <button class="btn primary" type="submit">Buscar</button>
      </form>
      <p class="facts"><b>{len(entries)}</b> descubrimientos <i>·</i> <b>{n_conf}</b> confirmados <i>·</i> <b>{len(by_cat)}</b> categorías</p>
    </div>
  </div>
  {_explorer(by_zone, zones)}
</div></section>
{_recent(entries, top_slugs)}
{_top(week)}
{_categories(by_cat)}
{_community(updated, n_comm)}
<section class="final"><div class="wrap">
  <h2>¿Qué secreto te falta descubrir?</h2>
  <div class="final-actions">
    <a class="btn primary lg" href="mapa/">Explorar el mapa</a>
    <a class="btn ghost lg" href="descubrimientos/">Ver todos los descubrimientos</a>
  </div>
</div></section>
<script>
(() => {{
  const map = document.querySelector(".explorer");
  if (!map) return;
  const hl = (name, on) => map.querySelectorAll(`[data-area="${{CSS.escape(name)}}"]`).forEach(el => el.classList.toggle("hl", on));
  map.querySelectorAll(".ex-zones [data-area], .leonida [data-area]").forEach(el => {{
    el.addEventListener("mouseenter", () => hl(el.dataset.area, true));
    el.addEventListener("mouseleave", () => hl(el.dataset.area, false));
    el.addEventListener("focus", () => hl(el.dataset.area, true));
    el.addEventListener("blur", () => hl(el.dataset.area, false));
  }});
}})();
</script>"""


# ---------------------------------------------------------------- descubrimientos

def discover_body(entries: list[dict], by_cat: dict[str, list[dict]], root: str, js_ver: str) -> str:
    p = _p()
    ordered = sorted(entries, key=lambda e: e.get("published_at", ""), reverse=True)
    chips = ['<button class="chip" data-cat="todos" aria-pressed="true">Todos <small>' + str(len(entries)) + "</small></button>"]
    for k, items in sorted(by_cat.items(), key=lambda kv: -len(kv[1])):
        chips.append(f'<button class="chip" data-cat="{k}" style="--c:{p.CAT_COLOR[k]}" aria-pressed="false">'
                     f'{escape(p.CATS[k][1])} <small>{len(items)}</small></button>')
    return f"""<nav class="crumbs"><a href="{root}">Inicio</a> › Descubrimientos</nav>
<header class="page-head">
  <h1>Descubrimientos</h1>
  <p class="lead">Todos los secretos, guías y hallazgos de GTA 6 que reunimos hasta ahora, del más nuevo al más viejo.</p>
</header>
<div class="filters">
  <form class="search" role="search" onsubmit="return false">
    <label class="sr" for="q">Buscar</label>
    <svg viewBox="0 0 24 24" aria-hidden="true"><circle cx="11" cy="11" r="7"/><path d="m20 20-3.5-3.5"/></svg>
    <input id="q" name="q" type="search" placeholder="Buscá un secreto: muelle, Cheetah, dinero…" autocomplete="off">
  </form>
  <div class="chips" id="chips" role="toolbar" aria-label="Categorías">{"".join(chips)}</div>
</div>
<p class="d-meta" id="meta">{len(entries)} descubrimientos</p>
<div class="grid" id="grid">{"".join(card(e, root) for e in ordered[:24])}</div>
<div class="more"><button class="btn" id="more"{"" if len(entries) > 24 else " hidden"}>Ver más</button></div>
<script src="{root}discover.js?v={js_ver}" defer></script>"""


# ---------------------------------------------------------------- mi lista (progreso)

def checklist_body(entries: list[dict], by_cat: dict[str, list[dict]], root: str) -> str:
    """Lista de todos los secretos para tildar. El progreso se guarda en el navegador (localStorage)."""
    p = _p()
    groups = []
    for k, items in sorted(by_cat.items(), key=lambda kv: -len(kv[1])):
        slug, name = p.CATS[k]
        rows = "".join(
            f'<li><label><input type="checkbox" data-slug="{escape(e["slug"])}">'
            f'<span class="ck-t"><a href="{root}d/{e["slug"]}/">{escape(e.get("titulo", ""))}</a>'
            + (f'<small>{escape(e.get("macro") or e.get("region"))}</small>' if (e.get("macro") or e.get("region")) else "")
            + "</span></label></li>"
            for e in sorted(items, key=lambda e: -int(e.get("popularity") or 0)))
        groups.append(f'<section class="ck-group" style="--c:{p.CAT_COLOR[k]}">'
                      f'<h2><a href="{root}c/{slug}/">{escape(name)}</a><span class="ck-n" data-total="{len(items)}">0 / {len(items)}</span></h2>'
                      f'<div class="ck-bar"><i></i></div><ul class="ck-list">{rows}</ul></section>')
    return f"""<nav class="crumbs"><a href="{root}">Inicio</a> › Mi lista</nav>
<header class="page-head"><h1>Mi lista de secretos</h1>
<p class="lead">Tildá los secretos que ya encontraste en tu partida y mirá cuánto te falta. Se guarda solo en este navegador: no hace falta registrarse.</p></header>
<div class="ck-summary"><p><b id="ck-done">0</b> de <b>{len(entries)}</b> secretos encontrados</p><div class="ck-bar big"><i id="ck-all"></i></div>
<div class="ck-actions"><label class="ck-hide"><input type="checkbox" id="ck-hide"> Ocultar los que ya hice</label><button class="btn sm ghost" id="ck-reset" type="button">Borrar mi progreso</button></div></div>
{"".join(groups)}
<script>
(() => {{
  const KEY = "wm-hechos";
  let done;
  try {{ done = new Set(JSON.parse(localStorage.getItem(KEY) || "[]")); }} catch {{ done = new Set(); }}
  const save = () => {{ try {{ localStorage.setItem(KEY, JSON.stringify([...done])); }} catch {{}} }};
  const boxes = [...document.querySelectorAll(".ck-list input")];
  function paint() {{
    boxes.forEach(b => {{ b.checked = done.has(b.dataset.slug); b.closest("li").classList.toggle("is-done", b.checked); }});
    let total = 0;
    document.querySelectorAll(".ck-group").forEach(g => {{
      const all = g.querySelectorAll(".ck-list input").length, n = g.querySelectorAll(".ck-list input:checked").length;
      total += n;
      g.querySelector(".ck-n").textContent = `${{n}} / ${{all}}`;
      g.querySelector(".ck-bar i").style.width = (100 * n / all) + "%";
    }});
    document.getElementById("ck-done").textContent = total;
    document.getElementById("ck-all").style.width = (100 * total / boxes.length) + "%";
  }}
  boxes.forEach(b => b.addEventListener("change", () => {{ b.checked ? done.add(b.dataset.slug) : done.delete(b.dataset.slug); save(); paint(); }}));
  document.getElementById("ck-hide").addEventListener("change", ev => document.body.classList.toggle("ck-hiding", ev.target.checked));
  document.getElementById("ck-reset").addEventListener("click", () => {{
    if (confirm("¿Borrar todo tu progreso? No se puede deshacer.")) {{ done.clear(); save(); paint(); }}
  }});
  paint();
}})();
</script>"""
