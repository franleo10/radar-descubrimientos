"""Descubrimientos quitados desde el panel de administración.

El panel guarda la lista en la base del sitio y la publica en /api/removed. En cada corrida:
- los que están en la lista salen de docs/data.json (y por eso de todas las páginas) y se
  guardan completos en state/removed.json;
- los que se restauraron en el panel vuelven a publicarse tal como estaban.

Si /api/removed no responde, no se toca nada: mejor dejar todo como está que restaurar por error.
El video de origen ya está en state/seen.json, así que el bot no lo vuelve a agregar.
"""
from __future__ import annotations

import requests

from . import config

REMOVED_FILE = config.ROOT / "state" / "removed.json"


def fetch_removed() -> set[str] | None:
    try:
        r = requests.get(f"{config.SITE_URL}/api/removed", timeout=20)
        if r.status_code != 200:
            return None
        return set(r.json()["removed"])
    except (requests.RequestException, ValueError, KeyError):
        return None


def apply(entries: list[dict], removed: set[str] | None = None) -> list[dict]:
    """Devuelve las entradas que quedan publicadas y actualiza state/removed.json."""
    from .main import load_json, save_json

    if removed is None:
        removed = fetch_removed()
    if removed is None:
        print("[quitados] no se pudo leer la lista; no se cambia nada")
        return entries
    stored: dict[str, dict] = load_json(REMOVED_FILE, {})
    keep, out = [], 0
    for e in entries:
        if e.get("slug") in removed:
            stored[e["slug"]] = e
            out += 1
        else:
            keep.append(e)
    back = [slug for slug in stored if slug not in removed]
    keep += [stored.pop(slug) for slug in back]
    if out or back:
        save_json(REMOVED_FILE, stored)
        print(f"[quitados] {out} sacados, {len(back)} restaurados ({len(stored)} quitados en total)")
    return keep
