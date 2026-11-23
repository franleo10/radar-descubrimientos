"""Publica los mejores descubrimientos nuevos en Telegram y Bluesky.

En cada corrida elige unos pocos descubrimientos confirmados, sin spoilers y
recientes que todavía no se publicaron, empezando por los más vistos. Lo ya
publicado queda guardado en state/posted.json para no repetir.

Cada red se saltea sola si no tiene sus claves cargadas.
"""
from __future__ import annotations

import html
import json
import re
from datetime import datetime, timedelta, timezone

import requests

from . import config

TIMEOUT = 20
POSTED_FILE = config.ROOT / "state" / "posted.json"
HASHTAGS = ["GTA6", "GTAVI"]
CAT_EMOJI = {
    "easter_egg": "🥚", "ubicacion_secreta": "🗺️", "coleccionable": "💎", "vehiculo": "🚗",
    "arma": "🔫", "dinero": "💰", "mision": "🎯", "mecanica_truco": "🎮", "otro": "📍",
}


def _load_posted() -> dict[str, list[str]]:
    try:
        return json.loads(POSTED_FILE.read_text(encoding="utf-8"))
    except (FileNotFoundError, json.JSONDecodeError):
        return {}


def _save_posted(data: dict[str, list[str]]) -> None:
    POSTED_FILE.parent.mkdir(parents=True, exist_ok=True)
    trimmed = {k: v[-5000:] for k, v in data.items()}
    POSTED_FILE.write_text(json.dumps(trimmed, ensure_ascii=False, indent=1), encoding="utf-8")


def pick(entries: list[dict], already: set[str], limit: int) -> list[dict]:
    since = (datetime.now(timezone.utc) - timedelta(days=config.SOCIAL_MAX_AGE_DAYS)).strftime("%Y-%m-%dT%H:%M:%SZ")
    ok = [e for e in entries
          if e.get("confianza") == "alta" and not e.get("spoiler") and not e.get("demo")
          and e.get("slug") and e["id"] not in already and e.get("published_at", "") >= since]
    ok.sort(key=lambda e: e.get("popularity") or 0, reverse=True)
    return ok[:limit]


def _url(e: dict) -> str:
    return f"{config.SITE_URL}/d/{e['slug']}/"


def _thumb(e: dict) -> str:
    if e.get("thumbnail"):
        return e["thumbnail"]
    return f"https://i.ytimg.com/vi/{e['video_id']}/hqdefault.jpg" if e.get("video_id") else ""


def _cut(text: str, limit: int) -> str:
    text = re.sub(r"\s+", " ", text or "").strip()
    return text if len(text) <= limit else text[: limit - 1].rsplit(" ", 1)[0].rstrip(",.;:") + "…"


# ---------------------------------------------------------------- Telegram --

def post_telegram(e: dict) -> bool:
    emoji = CAT_EMOJI.get(e.get("categoria"), "📍")
    lines = [f"{emoji} <b>{html.escape(e.get('titulo', ''))}</b>", "", html.escape(_cut(e.get("resumen", ""), 600))]
    if e.get("region"):
        lines += ["", f"📍 {html.escape(e['region'])}"]
    lines += ["", " ".join(f"#{t}" for t in HASHTAGS)]
    payload = {
        "chat_id": config.TELEGRAM_CHAT_ID,
        "caption": "\n".join(lines)[:1024],
        "parse_mode": "HTML",
        "reply_markup": json.dumps({"inline_keyboard": [[{"text": "Ver la guía completa →", "url": _url(e)}]]}),
    }
    base = f"https://api.telegram.org/bot{config.TELEGRAM_BOT_TOKEN}"
    thumb = _thumb(e)
    if thumb:
        r = requests.post(f"{base}/sendPhoto", data={**payload, "photo": thumb}, timeout=TIMEOUT)
    else:
        payload["text"] = payload.pop("caption")
        r = requests.post(f"{base}/sendMessage", data=payload, timeout=TIMEOUT)
    if r.status_code != 200:
        # No mostramos la URL: lleva el token adentro.
        print(f"[telegram] error {r.status_code}: {r.text[:200]}")
        return False
    return True


# ----------------------------------------------------------------- Bluesky --

class Bluesky:
    PDS = "https://bsky.social/xrpc"

    def __init__(self) -> None:
        r = requests.post(f"{self.PDS}/com.atproto.server.createSession",
                          json={"identifier": config.BLUESKY_HANDLE, "password": config.BLUESKY_APP_PASSWORD},
                          timeout=TIMEOUT)
        r.raise_for_status()
        s = r.json()
        self.did, self.headers = s["did"], {"Authorization": f"Bearer {s['accessJwt']}"}

    def _upload_thumb(self, url: str):
        try:
            img = requests.get(url, timeout=TIMEOUT)
            if img.status_code != 200 or len(img.content) > 950_000:
                return None
            r = requests.post(f"{self.PDS}/com.atproto.repo.uploadBlob", data=img.content,
                              headers={**self.headers, "Content-Type": "image/jpeg"}, timeout=TIMEOUT)
            return r.json().get("blob") if r.status_code == 200 else None
        except requests.RequestException:
            return None

    def post(self, e: dict) -> bool:
        emoji = CAT_EMOJI.get(e.get("categoria"), "📍")
        tags = " ".join(f"#{t}" for t in HASHTAGS)
        head = f"{emoji} {e.get('titulo', '')}\n\n"
        room = 290 - len(head) - len(tags) - 2
        text = f"{head}{_cut(e.get('resumen', ''), max(room, 40))}\n\n{tags}"
        facets = []
        for t in HASHTAGS:  # los hashtags necesitan posiciones en bytes UTF-8
            i = text.rfind(f"#{t}")
            start = len(text[:i].encode("utf-8"))
            facets.append({"index": {"byteStart": start, "byteEnd": start + len(f"#{t}".encode("utf-8"))},
                           "features": [{"$type": "app.bsky.richtext.facet#tag", "tag": t}]})
        external = {"uri": _url(e), "title": f"{e.get('titulo', '')} | WastedMap",
                    "description": _cut(e.get("resumen", ""), 280)}
        blob = self._upload_thumb(_thumb(e)) if _thumb(e) else None
        if blob:
            external["thumb"] = blob
        record = {"$type": "app.bsky.feed.post", "text": text, "facets": facets, "langs": ["es"],
                  "createdAt": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
                  "embed": {"$type": "app.bsky.embed.external", "external": external}}
        r = requests.post(f"{self.PDS}/com.atproto.repo.createRecord", headers=self.headers,
                          json={"repo": self.did, "collection": "app.bsky.feed.post", "record": record},
                          timeout=TIMEOUT)
        if r.status_code != 200:
            print(f"[bluesky] error {r.status_code}: {r.text[:200]}")
            return False
        return True


# ------------------------------------------------------------------- todo --

def publish(entries: list[dict]) -> None:
    posted = _load_posted()
    limit = config.SOCIAL_PER_RUN

    if config.TELEGRAM_BOT_TOKEN and config.TELEGRAM_CHAT_ID:
        done = posted.setdefault("telegram", [])
        sent = 0
        for e in pick(entries, set(done), limit):
            try:
                if post_telegram(e):
                    done.append(e["id"])
                    sent += 1
            except requests.RequestException as err:
                print(f"[telegram] sin conexión ({type(err).__name__})")
                break
        print(f"[telegram] {sent} publicados")
    else:
        print("[telegram] sin claves, se saltea")

    if config.BLUESKY_HANDLE and config.BLUESKY_APP_PASSWORD:
        done = posted.setdefault("bluesky", [])
        sent = 0
        try:
            client = Bluesky()
            for e in pick(entries, set(done), limit):
                if client.post(e):
                    done.append(e["id"])
                    sent += 1
        except requests.RequestException as err:
            print(f"[bluesky] no se pudo publicar ({type(err).__name__})")
        print(f"[bluesky] {sent} publicados")
    else:
        print("[bluesky] sin claves, se saltea")

    _save_posted(posted)
