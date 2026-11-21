"""Corre el bot completo: recolectar -> clasificar -> guardar docs/data.json.

Uso:
  python -m bot.main          corrida real (necesita las claves en .env o en Secrets)
  python -m bot.main --demo   datos de ejemplo, sin llamar a ninguna API
"""
from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone

from . import config


def load_json(path, default):
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (FileNotFoundError, json.JSONDecodeError):
        return default


def save_json(path, data) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=1), encoding="utf-8")


def merge(existing: list[dict], new: list[dict]) -> list[dict]:
    by_id = {e["id"]: e for e in existing}
    for n in new:
        by_id[n["id"]] = n
    entries = sorted(by_id.values(), key=lambda e: e.get("published_at", ""), reverse=True)
    return entries[: config.MAX_ENTRIES]


def run(demo: bool) -> None:
    site = load_json(config.DATA_FILE, {"entries": []})
    # Los datos de ejemplo se borran apenas corre el bot de verdad.
    existing = [e for e in site.get("entries", []) if not e.get("demo")]

    if demo:
        from .demo_data import CANDIDATES, CLASSIFICATIONS

        candidates = CANDIDATES
        results = CLASSIFICATIONS
        existing = []
    else:
        from .classify import Classifier
        from .collect import collect_reddit, collect_youtube

        seen: list[str] = load_json(config.STATE_FILE, [])
        seen_set = set(seen)
        candidates = [c for c in collect_youtube() + collect_reddit() if c["id"] not in seen_set]
        print(f"[bot] {len(candidates)} candidatos nuevos para clasificar")
        results, done = Classifier().classify(candidates) if candidates else ({}, set())
        # Guardamos solo los últimos 20.000 ids para que el archivo no crezca para siempre.
        save_json(config.STATE_FILE, (seen + sorted(done - seen_set))[-20000:])

    new_entries = []
    for c in candidates:
        r = results.get(c["id"])
        if not r or not r["relevante"] or r["confianza"] == "baja":
            continue
        entry = {k: v for k, v in c.items() if k != "text"}
        entry.update({k: v for k, v in r.items() if k not in ("id", "relevante")})
        if demo:
            entry["demo"] = True
        new_entries.append(entry)

    entries = merge(existing, new_entries)
    save_json(
        config.DATA_FILE,
        {
            "site_name": config.SITE_NAME,
            "updated_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
            "entries": entries,
        },
    )
    print(f"[bot] {len(new_entries)} descubrimientos nuevos, {len(entries)} en total")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--demo", action="store_true", help="usar datos de ejemplo")
    run(ap.parse_args().demo)
