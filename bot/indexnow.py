"""Avisa a Bing (y a los demás buscadores de IndexNow) qué páginas son nuevas o cambiaron.

La clave es pública a propósito: está en docs/<clave>.txt para que el buscador compruebe que el
aviso viene del dueño del sitio. Solo se mandan las URLs del sitemap que no se avisaron antes o
cuya fecha cambió; lo ya avisado se guarda en state/indexnow.json.

Uso manual: python -m bot.indexnow          (avisa lo pendiente)
            python -m bot.indexnow --todo   (vuelve a avisar todo el sitemap)
"""
from __future__ import annotations

import json
import re
import sys
from urllib.parse import urlparse

import requests

from . import config

KEY = "11b293e5193f586476322108e01d3c99"
ENDPOINT = "https://api.indexnow.org/indexnow"
STATE = config.ROOT / "state" / "indexnow.json"
BATCH = 10000  # máximo por aviso


def sitemap_urls() -> dict[str, str]:
    xml = (config.DOCS_DIR / "sitemap.xml").read_text(encoding="utf-8")
    out = {}
    for block in re.findall(r"<url>(.*?)</url>", xml, re.S):
        loc = re.search(r"<loc>(.*?)</loc>", block)
        mod = re.search(r"<lastmod>(.*?)</lastmod>", block)
        if loc:
            out[loc.group(1).replace("&amp;", "&")] = mod.group(1) if mod else ""
    return out


def submit(everything: bool = False) -> None:
    if urlparse(config.SITE_URL).hostname in (None, "localhost", "127.0.0.1"):
        return
    current = sitemap_urls()
    try:
        sent = {} if everything else json.loads(STATE.read_text(encoding="utf-8"))
    except (FileNotFoundError, json.JSONDecodeError):
        sent = {}
    todo = [u for u, m in current.items() if sent.get(u) != m]
    if not todo:
        print("[indexnow] nada nuevo para avisar")
        return
    host = urlparse(config.SITE_URL).hostname
    ok = 0
    for i in range(0, len(todo), BATCH):
        part = todo[i:i + BATCH]
        try:
            r = requests.post(ENDPOINT, timeout=30, json={
                "host": host, "key": KEY, "keyLocation": f"{config.SITE_URL}/{KEY}.txt", "urlList": part,
            })
        except requests.RequestException as err:
            print(f"[indexnow] no se pudo avisar ({type(err).__name__})")
            break
        # 200 = recibido, 202 = recibido y la clave se valida después
        if r.status_code not in (200, 202):
            print(f"[indexnow] respuesta {r.status_code}: {r.text[:200]}")
            break
        for u in part:
            sent[u] = current[u]
        ok += len(part)
    # se olvidan las URLs que ya no están en el sitemap (por ejemplo, descubrimientos quitados)
    sent = {u: m for u, m in sent.items() if u in current}
    STATE.parent.mkdir(parents=True, exist_ok=True)
    STATE.write_text(json.dumps(sent, ensure_ascii=False, indent=0), encoding="utf-8")
    print(f"[indexnow] {ok} páginas avisadas a Bing y compañía")


if __name__ == "__main__":
    submit(everything="--todo" in sys.argv)
