"""Versión en portugués de Brasil (/pt/).

- translate(): traduce de a poco las guías (título, resumen, explicación y pasos) con Claude y
  guarda el resultado en e["pt"]. Si la guía en español cambia, se vuelve a traducir.
- build(): genera /pt/, /pt/c/<categoría>/ y /pt/d/<guía>/ solo con lo que ya está traducido.
"""
from __future__ import annotations

import hashlib
import json
from html import escape

import anthropic

from . import config
from .classify import model_extras

PT_CATS = {
    "easter_egg": ("easter-eggs", "Easter eggs", "Easter eggs de GTA 6: todos os segredos encontrados"),
    "ubicacion_secreta": ("lugares-secretos", "Lugares secretos", "Lugares secretos de GTA 6 e como chegar"),
    "coleccionable": ("colecionaveis", "Colecionáveis", "Colecionáveis de GTA 6: localizações e recompensas"),
    "vehiculo": ("veiculos", "Veículos", "Carros secretos e raros de GTA 6: onde encontrar"),
    "arma": ("armas", "Armas", "Armas secretas de GTA 6 e onde conseguir"),
    "dinero": ("dinheiro", "Dinheiro", "Como ganhar dinheiro rápido no GTA 6"),
    "mision": ("missoes", "Missões", "Missões secretas de GTA 6"),
    "mecanica_truco": ("truques-e-dicas", "Truques e dicas", "Truques e dicas de GTA 6"),
    "otro": ("outros", "Outros", "Outras descobertas de GTA 6"),
}

SYSTEM = """Você traduz para português do Brasil as guias do WastedMap, um site com os \
segredos do videogame GTA 6. O texto original está em espanhol rioplatense.

Regras:
- Tradução fiel e natural, no tom de um site de games brasileiro. Não acrescente nem invente nada.
- Mantenha como estão os nomes próprios: lugares (Vice City, Leonida, Port Gellhorn...), \
veículos, armas, personagens, missões e nomes de criadores.
- Devolva cada item com o mesmo "id". Se um campo vier vazio, devolva vazio."""

SCHEMA = {
    "type": "object",
    "properties": {"items": {"type": "array", "items": {
        "type": "object",
        "properties": {"id": {"type": "string"}, "titulo": {"type": "string"}, "resumen": {"type": "string"},
                       "detalle": {"type": "string"}, "pasos": {"type": "array", "items": {"type": "string"}}},
        "required": ["id", "titulo", "resumen", "detalle", "pasos"], "additionalProperties": False}}},
    "required": ["items"], "additionalProperties": False,
}


def _src(e: dict) -> str:
    raw = json.dumps([e.get("titulo"), e.get("resumen"), e.get("detalle"), e.get("pasos")], ensure_ascii=False)
    return hashlib.sha1(raw.encode()).hexdigest()[:10]


def translate(entries: list[dict]) -> None:
    from .pages import indexable

    todo = [e for e in entries if (e.get("pt") or {}).get("src") != _src(e)]
    # Primero lo que va a Google y lo más visto.
    todo.sort(key=lambda e: (not indexable(e), -int(e.get("popularity") or 0)))
    todo = todo[: config.TRANSLATE_PER_RUN]
    if not todo:
        return
    client = anthropic.Anthropic()
    done = 0
    for i in range(0, len(todo), 10):
        batch = todo[i:i + 10]
        payload = [{"id": e["id"], "titulo": e.get("titulo", ""), "resumen": e.get("resumen", ""),
                    "detalle": e.get("detalle", ""), "pasos": e.get("pasos") or []} for e in batch]
        try:
            response = client.beta.messages.create(
                model=config.CLAUDE_MODEL, max_tokens=16000, **model_extras(),
                output_config={"effort": "low", "format": {"type": "json_schema", "schema": SCHEMA}},
                system=SYSTEM,
                messages=[{"role": "user", "content": json.dumps(payload, ensure_ascii=False)}],
            )
        except anthropic.APIError as err:
            print(f"[pt] no se pudo traducir ({type(err).__name__})")
            break
        if response.stop_reason in ("refusal", "max_tokens"):
            continue
        text = next(b.text for b in response.content if b.type == "text")
        by_id = {r["id"]: r for r in json.loads(text)["items"]}
        for e in batch:
            r = by_id.get(e["id"])
            if r and r["titulo"].strip():
                e["pt"] = {"titulo": r["titulo"].strip(), "resumen": r["resumen"].strip(),
                           "detalle": r["detalle"].strip(), "pasos": [p.strip() for p in r["pasos"] if p.strip()],
                           "src": _src(e)}
                done += 1
    left = sum(1 for e in entries if (e.get("pt") or {}).get("src") != _src(e))
    print(f"[pt] {done} guías traducidas, {left} pendientes")


# ---------------------------------------------------------------- páginas

def _cat(e):
    k = e.get("categoria") if e.get("categoria") in PT_CATS else "otro"
    return k, PT_CATS[k]


def _card(e: dict, root: str, thumb: str) -> str:
    from .pages import CAT_COLOR
    k, (slug, name, _) = _cat(e)
    t = e["pt"]
    img = f'<img loading="lazy" src="{escape(thumb)}" alt="">' if thumb else ""
    return (f'<article class="card"><a class="thumb" href="{root}pt/d/{e["slug"]}/" tabindex="-1" aria-hidden="true">{img}</a>'
            f'<div class="card-body"><div class="meta"><a class="m-cat" style="--c:{CAT_COLOR[k]}" href="{root}pt/c/{slug}/">{name}</a>'
            + (f'<span>{escape(e["macro"])}</span>' if e.get("macro") else "") +
            f'</div><h3><a href="{root}pt/d/{e["slug"]}/">{escape(t["titulo"])}</a></h3><p>{escape(t["resumen"])}</p></div></article>')


def _entry(e: dict, P) -> str:
    root = "../../../"
    t = e["pt"]
    k, (slug, name, _) = _cat(e)
    url = f"{config.SITE_URL}/pt/d/{e['slug']}/"
    es_url = f"{config.SITE_URL}/d/{e['slug']}/"
    thumb = P._thumb(e)
    media = ""
    if e.get("video_id"):
        media = (f'<button class="media" data-yt="{escape(e["video_id"])}" aria-label="Reproduzir vídeo">'
                 f'<img src="{escape(thumb)}" alt="{escape(t["titulo"])}"><span class="play"></span></button>')
    steps = ("<h2>Como fazer</h2><ol class=\"steps\">" + "".join(f"<li>{escape(p)}</li>" for p in t["pasos"]) + "</ol>"
             if t["pasos"] else "")
    detail = ("<h2>O que é</h2>" + "".join(f"<p>{escape(x.strip())}</p>" for x in t["detalle"].split("\n\n") if x.strip())
              if t["detalle"] else "")
    flag = '<span class="tag warn">Não confirmado</span>' if e.get("confianza") == "media" else ""
    spoiler_btn = '<button class="spoiler-btn">Contém spoilers · toque para ver</button>' if e.get("spoiler") else ""
    body = f"""<nav class="crumbs"><a href="{root}pt/">Início</a> › <a href="{root}pt/c/{slug}/">{name}</a></nav>
<article class="entry">
  <div class="tags"><a class="tag cat" style="--c:{P.CAT_COLOR[k]}" href="{root}pt/c/{slug}/">{name}</a>{flag}</div>
  {spoiler_btn}
  <div class="{"spoiler" if e.get("spoiler") else ""}">
    <h1>{escape(t["titulo"])}</h1>
    {media}
    <p class="lead">{escape(t["resumen"])}</p>
    {detail}{steps}
  </div>
  <h2>Fonte</h2><ul class="sources"><li><a href="{escape(e.get("url", ""))}" rel="noopener">{escape(e.get("author", ""))}</a></li></ul>
  <p class="note">Resumo feito automaticamente a partir do vídeo original e traduzido do espanhol. Para votar e comentar, veja a <a href="{root}d/{e['slug']}/">versão em espanhol</a>.</p>
</article>"""
    return P._layout(title=f"{t['titulo']} | GTA 6", description=t["resumen"][:300], canonical=url, root=root,
                     body=body, image=thumb, noindex=not P.indexable(e), lang="pt",
                     alternates=[("es", es_url), ("pt-BR", url)])


def build(entries: list[dict], P) -> list[tuple[str, str]]:
    """Genera las páginas en portugués. Devuelve (url, fecha) para el sitemap."""
    docs = config.DOCS_DIR
    import shutil
    shutil.rmtree(docs / "pt", ignore_errors=True)
    done = [e for e in entries if (e.get("pt") or {}).get("titulo")]
    if not done:
        return []
    urls = []
    for e in done:
        out = docs / "pt" / "d" / e["slug"] / "index.html"
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(_entry(e, P), encoding="utf-8")
        if P.indexable(e):
            urls.append((f"{config.SITE_URL}/pt/d/{e['slug']}/", e.get("published_at", "")))

    by_cat: dict[str, list[dict]] = {}
    for e in done:
        by_cat.setdefault(_cat(e)[0], []).append(e)
    for k, items in by_cat.items():
        slug, name, h1 = PT_CATS[k]
        root = "../../../"
        items = sorted(items, key=lambda e: -int(e.get("popularity") or 0))
        body = (f'<nav class="crumbs"><a href="{root}pt/">Início</a> › {name}</nav>'
                f'<header class="page-head"><h1>{escape(h1)}</h1><p class="lead">{len(items)} descobertas da comunidade, '
                f'com os passos e o vídeo original. Atualizado várias vezes por dia.</p></header>'
                f'<div class="grid">{"".join(_card(e, root, P._thumb(e)) for e in items)}</div>')
        out = docs / "pt" / "c" / slug / "index.html"
        out.parent.mkdir(parents=True, exist_ok=True)
        url = f"{config.SITE_URL}/pt/c/{slug}/"
        out.write_text(P._layout(title=f"{h1} | {config.SITE_NAME}", description=h1, canonical=url, root=root,
                                 body=body, lang="pt", wide=True), encoding="utf-8")
        urls.append((url, items[0].get("published_at", "")))

    root = "../"
    recent = sorted(done, key=lambda e: e.get("published_at", ""), reverse=True)
    cats = "".join(f'<li class="t3" style="--c:{P.CAT_COLOR[k]}"><a href="{root}pt/c/{PT_CATS[k][0]}/"><span class="cn">{PT_CATS[k][1]}</span>'
                   f'<span class="cc">{len(v)}</span><span class="arr" aria-hidden="true">→</span></a></li>'
                   for k, v in sorted(by_cat.items(), key=lambda kv: -len(kv[1])))
    body = f"""<header class="page-head pt-hero">
  <p class="overline">Guia não oficial · atualizado várias vezes por dia</p>
  <h1>Todos os segredos de GTA&nbsp;6 em <em>um só mapa</em></h1>
  <p class="lead">Easter eggs, lugares escondidos, carros raros e guias que a comunidade descobre, resumidos em português e com o vídeo original.</p>
  <p class="pt-actions"><a class="btn primary" href="{root}mapa/">Abrir o mapa</a><a class="btn" href="{root}">Ver em espanhol ({len(entries)} guias)</a></p>
</header>
<h2 id="categorias">Por tipo de descoberta</h2>
<ul class="cats">{cats}</ul>
<h2>Descobertas recentes</h2>
<div class="grid">{"".join(_card(e, root, P._thumb(e)) for e in recent[:24])}</div>"""
    out = docs / "pt" / "index.html"
    out.write_text(P._layout(title=f"{config.SITE_NAME} · Segredos, easter eggs e mapa de GTA 6",
                             description="Segredos, easter eggs, lugares escondidos e guias de GTA 6 que a comunidade encontra. Guia não oficial.",
                             canonical=f"{config.SITE_URL}/pt/", root=root, body=body, lang="pt", wide=True,
                             og_type="website", alternates=[("es", f"{config.SITE_URL}/"), ("pt-BR", f"{config.SITE_URL}/pt/")]),
                   encoding="utf-8")
    urls.insert(0, (f"{config.SITE_URL}/pt/", recent[0].get("published_at", "")))
    print(f"[web] {len(done)} páginas en portugués")
    return urls
