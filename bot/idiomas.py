"""Versiones traducidas del sitio: portugués de Brasil (/pt/) e inglés (/en/).

- translate(entries, lang): traduce de a poco los descubrimientos (título, resumen, explicación y
  pasos) con Claude y guarda el resultado en e[lang]. Si el texto en español cambia, se vuelve a traducir.
- build(entries, P, lang): genera /<lang>/, /<lang>/c/<categoría>/ y /<lang>/d/<descubrimiento>/
  solo con lo que ya está traducido.
"""
from __future__ import annotations

import hashlib
import json
import shutil
from html import escape

import anthropic

from . import config
from .classify import model_extras

LANGS = ("pt", "en")
HREFLANG = {"es": "es", "pt": "pt-BR", "en": "en"}

CATS = {
    "pt": {
        "easter_egg": ("easter-eggs", "Easter eggs", "Easter eggs de GTA 6: todos os segredos encontrados"),
        "ubicacion_secreta": ("lugares-secretos", "Lugares secretos", "Lugares secretos de GTA 6 e como chegar"),
        "coleccionable": ("colecionaveis", "Colecionáveis", "Colecionáveis de GTA 6: localizações e recompensas"),
        "vehiculo": ("veiculos", "Veículos", "Carros secretos e raros de GTA 6: onde encontrar"),
        "arma": ("armas", "Armas", "Armas secretas de GTA 6 e onde conseguir"),
        "dinero": ("dinheiro", "Dinheiro", "Como ganhar dinheiro rápido no GTA 6"),
        "mision": ("missoes", "Missões", "Missões secretas de GTA 6"),
        "mecanica_truco": ("truques-e-dicas", "Truques e dicas", "Truques e dicas de GTA 6"),
        "otro": ("outros", "Outros", "Outras descobertas de GTA 6"),
    },
    "en": {
        "easter_egg": ("easter-eggs", "Easter eggs", "GTA 6 easter eggs: every secret found so far"),
        "ubicacion_secreta": ("secret-locations", "Secret locations", "GTA 6 secret locations and how to get there"),
        "coleccionable": ("collectibles", "Collectibles", "GTA 6 collectibles: locations and rewards"),
        "vehiculo": ("vehicles", "Vehicles", "GTA 6 secret and rare cars: where to find them"),
        "arma": ("weapons", "Weapons", "GTA 6 secret weapons and where to get them"),
        "dinero": ("money", "Money", "How to make money fast in GTA 6"),
        "mision": ("missions", "Missions", "GTA 6 secret missions"),
        "mecanica_truco": ("tips-and-tricks", "Tips and tricks", "GTA 6 tips and tricks"),
        "otro": ("other", "Other", "Other GTA 6 discoveries"),
    },
}

SYSTEM = {
    "pt": """Você traduz para português do Brasil as guias do WastedMap, um site com os \
segredos do videogame GTA 6. O texto original está em espanhol rioplatense.

Regras:
- Tradução fiel e natural, no tom de um site de games brasileiro. Não acrescente nem invente nada.
- Mantenha como estão os nomes próprios: lugares (Vice City, Leonida, Port Gellhorn...), \
veículos, armas, personagens, missões e nomes de criadores.
- Devolva cada item com o mesmo "id". Se um campo vier vazio, devolva vazio.""",
    "en": """You translate WastedMap's guides into English. WastedMap is a site about the \
secrets of the video game GTA 6. The original text is in Rioplatense Spanish.

Rules:
- Faithful, natural translation in the tone of an English-language gaming site. Do not add or invent anything.
- Keep proper names as they are: places (Vice City, Leonida, Port Gellhorn...), vehicles, \
weapons, characters, missions and creator names.
- Return each item with the same "id". If a field is empty, return it empty.""",
}

# Textos fijos de las páginas.
TXT = {
    "pt": dict(
        play="Reproduzir vídeo", how="Como fazer", what="O que é", unconfirmed="Não confirmado",
        spoiler="Contém spoilers · toque para ver", source="Fonte", home="Início",
        note='Resumo feito automaticamente a partir do vídeo original e traduzido do espanhol. Para votar e comentar, veja a <a href="{es}">versão em espanhol</a>.',
        cat_lead="{n} descobertas da comunidade, com os passos e o vídeo original. Atualizado várias vezes por dia.",
        overline="Guia de GTA 6 em português · atualizado todo dia",
        h1="Os segredos de GTA&nbsp;6, <em>explicados passo a passo</em>",
        lead="Todo dia juntamos os easter eggs, lugares escondidos, carros raros e formas de ganhar dinheiro que a galera descobre no jogo, e mostramos <b>onde estão e como conseguir</b>, com o vídeo original. Grátis e sem cadastro.",
        do=[("Procure um segredo", "Cada um tem seu guia: o que é, onde fica e o passo a passo, com o vídeo de quem encontrou.", "#recentes", "Ver os segredos"),
              ("Veja no mapa", "Descubra em que região de Leonida fica cada um e o que tem perto de onde você está jogando.", "{root}pt/mapa/", "Abrir o mapa"),
              ("Acompanhe seu progresso", "Marque o que já fez e veja quanto falta: lista dos 100 %, troféus e truques.", "{root}pt/100-por-cento/", "Lista dos 100 %")],
        what_aria="O que dá para fazer no WastedMap", sample_tag="Assim é cada guia", sample_more="Ver o guia completo", sample_n="mais {n} passos",
        open_map="Abrir o mapa", see_es="Ver em espanhol ({n} guias)",
        by_type="Por tipo de descoberta", recent="Descobertas recentes",
        soon="As descobertas da comunidade estão sendo traduzidas e aparecem aqui aos poucos.",
        title="Segredos de GTA 6 explicados passo a passo | {site}",
        desc="Easter eggs, lugares escondidos, carros raros e formas de ganhar dinheiro no GTA 6: onde estão e como conseguir, passo a passo e com o vídeo original. Em português, grátis e atualizado todo dia.",
    ),
    "en": dict(
        play="Play video", how="How to do it", what="What it is", unconfirmed="Unconfirmed",
        spoiler="Contains spoilers · tap to reveal", source="Source", home="Home",
        note='Summary written automatically from the original video and translated from Spanish. To vote and comment, see the <a href="{es}">Spanish version</a>.',
        cat_lead="{n} community discoveries, with the steps and the original video. Updated several times a day.",
        overline="GTA 6 guide · updated every day",
        h1="GTA&nbsp;6 secrets, <em>explained step by step</em>",
        lead="Every day we gather the easter eggs, hidden places, rare cars and money methods players find in the game, and tell you <b>where they are and how to get them</b>, with the original video. Free, no sign-up.",
        do=[("Look up a secret", "Each one has its own guide: what it is, where it is and the steps to get it, with the video from whoever found it.", "#recentes", "See the secrets"),
              ("Find it on the map", "See which part of Leonida each one is in and what is near where you are playing.", "{root}en/mapa/", "Open the map"),
              ("Track your progress", "Tick off what you have done and see what is left: 100% checklist, trophies and cheats.", "{root}en/100-percent/", "100% checklist")],
        what_aria="What you can do on WastedMap", sample_tag="What every guide looks like", sample_more="Read the full guide", sample_n="{n} more steps",
        open_map="Open the map", see_es="See it in Spanish ({n} discoveries)",
        by_type="By type of discovery", recent="Latest discoveries",
        soon="Community discoveries are being translated and will show up here bit by bit.",
        title="GTA 6 secrets explained step by step | {site}",
        desc="Easter eggs, hidden places, rare cars and money methods in GTA 6: where they are and how to get them, step by step with the original video. Free and updated every day.",
    ),
}

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


def translated(e: dict, lang: str) -> bool:
    return bool((e.get(lang) or {}).get("titulo"))


def alternates(e: dict) -> list[tuple[str, str]]:
    """Versiones de un descubrimiento que existen, para los enlaces hreflang."""
    out = [("es", f"{config.SITE_URL}/d/{e['slug']}/")]
    out += [(HREFLANG[l], f"{config.SITE_URL}/{l}/d/{e['slug']}/") for l in LANGS if translated(e, l)]
    return out


def translate(entries: list[dict], lang: str) -> None:
    from .pages import indexable

    todo = [e for e in entries if (e.get(lang) or {}).get("src") != _src(e)]
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
                system=SYSTEM[lang],
                messages=[{"role": "user", "content": json.dumps(payload, ensure_ascii=False)}],
            )
        except anthropic.APIError as err:
            print(f"[{lang}] no se pudo traducir ({type(err).__name__})")
            break
        if response.stop_reason in ("refusal", "max_tokens"):
            continue
        text = next(b.text for b in response.content if b.type == "text")
        by_id = {r["id"]: r for r in json.loads(text)["items"]}
        for e in batch:
            r = by_id.get(e["id"])
            if r and r["titulo"].strip():
                e[lang] = {"titulo": r["titulo"].strip(), "resumen": r["resumen"].strip(),
                           "detalle": r["detalle"].strip(), "pasos": [p.strip() for p in r["pasos"] if p.strip()],
                           "src": _src(e)}
                done += 1
    left = sum(1 for e in entries if (e.get(lang) or {}).get("src") != _src(e))
    print(f"[{lang}] {done} guías traducidas, {left} pendientes")


# ---------------------------------------------------------------- páginas

def _cat(e, lang):
    k = e.get("categoria") if e.get("categoria") in CATS[lang] else "otro"
    return k, CATS[lang][k]


def _card(e: dict, root: str, thumb: str, lang: str) -> str:
    from .pages import CAT_COLOR
    k, (slug, name, _) = _cat(e, lang)
    t = e[lang]
    img = f'<img loading="lazy" src="{escape(thumb)}" alt="">' if thumb else ""
    return (f'<article class="card"><a class="thumb" href="{root}{lang}/d/{e["slug"]}/" tabindex="-1" aria-hidden="true">{img}</a>'
            f'<div class="card-body"><div class="meta"><a class="m-cat" style="--c:{CAT_COLOR[k]}" href="{root}{lang}/c/{slug}/">{name}</a>'
            + (f'<span>{escape(e["macro"])}</span>' if e.get("macro") else "") +
            f'</div><h3><a href="{root}{lang}/d/{e["slug"]}/">{escape(t["titulo"])}</a></h3><p>{escape(t["resumen"])}</p></div></article>')


def _entry(e: dict, P, lang: str) -> str:
    root = "../../../"
    t, x = e[lang], TXT[lang]
    k, (slug, name, _) = _cat(e, lang)
    url = f"{config.SITE_URL}/{lang}/d/{e['slug']}/"
    thumb = P._thumb(e)
    media = ""
    if e.get("video_id"):
        media = (f'<button class="media" data-yt="{escape(e["video_id"])}" aria-label="{x["play"]}">'
                 f'<img src="{escape(thumb)}" alt="{escape(t["titulo"])}"><span class="play"></span></button>')
    steps = (f'<h2>{x["how"]}</h2><ol class="steps">' + "".join(f"<li>{escape(p)}</li>" for p in t["pasos"]) + "</ol>"
             if t["pasos"] else "")
    detail = (f'<h2>{x["what"]}</h2>' + "".join(f"<p>{escape(p.strip())}</p>" for p in t["detalle"].split("\n\n") if p.strip())
              if t["detalle"] else "")
    flag = f'<span class="tag warn">{x["unconfirmed"]}</span>' if e.get("confianza") == "media" else ""
    spoiler_btn = f'<button class="spoiler-btn">{x["spoiler"]}</button>' if e.get("spoiler") else ""
    body = f"""<nav class="crumbs"><a href="{root}{lang}/">{x["home"]}</a> › <a href="{root}{lang}/c/{slug}/">{name}</a></nav>
<article class="entry">
  <div class="tags"><a class="tag cat" style="--c:{P.CAT_COLOR[k]}" href="{root}{lang}/c/{slug}/">{name}</a>{flag}</div>
  {spoiler_btn}
  <div class="{"spoiler" if e.get("spoiler") else ""}">
    <h1>{escape(t["titulo"])}</h1>
    {media}
    <p class="lead">{escape(t["resumen"])}</p>
    {detail}{steps}
  </div>
  <h2>{x["source"]}</h2><ul class="sources"><li><a href="{escape(e.get("url", ""))}" rel="noopener">{escape(e.get("author", ""))}</a></li></ul>
  <p class="note">{x["note"].format(es=f"{root}d/{e['slug']}/")}</p>
</article>"""
    return P._layout(title=f"{t['titulo']} | GTA 6", description=t["resumen"][:300], canonical=url, root=root,
                     body=body, image=thumb, noindex=not P.indexable(e), lang=lang, alternates=alternates(e))


def build(entries: list[dict], P, lang: str) -> list[tuple[str, str]]:
    """Genera las páginas de un idioma. Devuelve (url, fecha) para el sitemap."""
    from .guias import home_section
    docs, x, cats = config.DOCS_DIR, TXT[lang], CATS[lang]
    shutil.rmtree(docs / lang, ignore_errors=True)
    done = [e for e in entries if translated(e, lang)]
    urls = []
    for e in done:
        out = docs / lang / "d" / e["slug"] / "index.html"
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(_entry(e, P, lang), encoding="utf-8")
        if P.indexable(e):
            urls.append((f"{config.SITE_URL}/{lang}/d/{e['slug']}/", e.get("published_at", "")))

    by_cat: dict[str, list[dict]] = {}
    for e in done:
        by_cat.setdefault(_cat(e, lang)[0], []).append(e)
    for k, items in by_cat.items():
        slug, name, h1 = cats[k]
        root = "../../../"
        items = sorted(items, key=lambda e: -int(e.get("popularity") or 0))
        body = (f'<nav class="crumbs"><a href="{root}{lang}/">{x["home"]}</a> › {name}</nav>'
                f'<header class="page-head"><h1>{escape(h1)}</h1><p class="lead">{x["cat_lead"].format(n=len(items))}</p></header>'
                f'<div class="grid">{"".join(_card(e, root, P._thumb(e), lang) for e in items)}</div>')
        out = docs / lang / "c" / slug / "index.html"
        out.parent.mkdir(parents=True, exist_ok=True)
        url = f"{config.SITE_URL}/{lang}/c/{slug}/"
        out.write_text(P._layout(title=f"{h1} | {config.SITE_NAME}", description=h1, canonical=url, root=root,
                                 body=body, lang=lang, wide=True), encoding="utf-8")
        urls.append((url, items[0].get("published_at", "")))

    # La portada del idioma sale siempre (tiene las guías), aunque todavía no haya nada traducido.
    root = "../"
    recent = sorted(done, key=lambda e: e.get("published_at", ""), reverse=True)
    cats_html = "".join(f'<li class="t3" style="--c:{P.CAT_COLOR[k]}"><a href="{root}{lang}/c/{cats[k][0]}/"><span class="cn">{cats[k][1]}</span>'
                        f'<span class="cc">{len(v)}</span><span class="arr" aria-hidden="true">→</span></a></li>'
                        for k, v in sorted(by_cat.items(), key=lambda kv: -len(kv[1])))
    found = (f'<h2 id="categorias">{x["by_type"]}</h2><ul class="cats">{cats_html}</ul>'
             f'<h2 id="recentes">{x["recent"]}</h2><div class="grid">{"".join(_card(e, root, P._thumb(e), lang) for e in recent[:24])}</div>'
             if done else f'<p class="note" id="categorias">{x["soon"]}</p>')
    body = f"""<header class="page-head pt-hero">
  <p class="overline">{x["overline"]}</p>
  <h1>{x["h1"]}</h1>
  <p class="lead lede">{x["lead"]}</p>
  <p class="pt-actions"><a class="btn primary" href="{root}{lang}/mapa/">{x["open_map"]}</a><a class="btn" href="{root}">{x["see_es"].format(n=len(entries))}</a></p>
</header>
{_what(x, root)}
{_sample(done, P, lang, root)}
{home_section(root, lang)}
{found}"""
    out = docs / lang / "index.html"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(P._layout(title=x["title"].format(site=config.SITE_NAME), description=x["desc"],
                             canonical=f"{config.SITE_URL}/{lang}/", root=root, body=body, lang=lang, wide=True,
                             og_type="website", alternates=home_alternates()), encoding="utf-8")
    urls.insert(0, (f"{config.SITE_URL}/{lang}/", recent[0].get("published_at", "") if recent else ""))
    print(f"[web] {len(done)} páginas en {lang}")
    return urls


def _what(x: dict, root: str) -> str:
    lis = "".join(f'<li><span class="wn">{i}</span><b>{t}</b><p>{d}</p><a href="{h.format(root=root)}">{c} <span aria-hidden="true">→</span></a></li>'
                  for i, (t, d, h, c) in enumerate(x["do"], 1))
    return f'<ol class="what" aria-label="{x["what_aria"]}">{lis}</ol>'


def _sample(done: list[dict], P, lang: str, root: str) -> str:
    """Una guía real ya traducida, resumida, para que se vea qué hay adentro."""
    pool = [e for e in done if len(e[lang].get("pasos") or []) >= 3 and P._thumb(e) and not e.get("spoiler")]
    if not pool:
        return ""
    e = max(pool, key=lambda e: (e.get("confianza") == "alta", e.get("popularity") or 0))
    t, x = e[lang], TXT[lang]
    k, (slug, name, _) = _cat(e, lang)
    url = f"{root}{lang}/d/{e['slug']}/"
    steps = "".join(f"<li>{escape(s)}</li>" for s in t["pasos"][:3])
    more = len(t["pasos"]) - 3
    extra = f" ({x['sample_n'].format(n=more)})" if more > 0 else ""
    return f"""<div class="sample">
  <p class="sample-tag">{x["sample_tag"]}</p>
  <a class="thumb" href="{url}" tabindex="-1" aria-hidden="true"><img loading="lazy" src="{escape(P._thumb(e))}" alt=""><span class="play"></span></a>
  <div class="sample-body">
    <div class="meta"><a class="m-cat" style="--c:{P.CAT_COLOR[k]}" href="{root}{lang}/c/{slug}/">{name}</a></div>
    <h3><a href="{url}">{escape(t["titulo"])}</a></h3>
    <p>{escape(t["resumen"])}</p>
    <ol class="sample-steps">{steps}</ol>
    <a class="more-link" href="{url}">{x["sample_more"]}{extra} <span aria-hidden="true">→</span></a>
  </div>
</div>"""


def home_alternates() -> list[tuple[str, str]]:
    return [("es", f"{config.SITE_URL}/")] + [(HREFLANG[l], f"{config.SITE_URL}/{l}/") for l in LANGS]
