"""Recolecta candidatos desde las APIs oficiales de YouTube y Reddit.

Solo se guardan metadatos (título, descripción, autor, enlace). Los videos no se
descargan: en la web se insertan con el reproductor oficial.
"""
from __future__ import annotations

import re
from datetime import datetime, timedelta, timezone

import requests

from . import config

TIMEOUT = 20


def _utc_iso(dt: datetime) -> str:
    return dt.astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


# ----------------------------------------------------------------- YouTube --

def collect_youtube() -> list[dict]:
    if not config.YOUTUBE_API_KEY:
        print("[youtube] sin YOUTUBE_API_KEY, se saltea")
        return []

    since = datetime.now(timezone.utc) - timedelta(hours=config.YOUTUBE_LOOKBACK_HOURS)
    ids: list[str] = []
    # El bot corre cada 2 horas: en cada corrida busca la mitad de las consultas (alternando),
    # así cada una se revisa cada 4 horas y la cuota diaria de YouTube alcanza con margen.
    half = (datetime.now(timezone.utc).hour // 2) % 2
    queries = config.YOUTUBE_QUERIES[half::2] if config.YOUTUBE_ROTATE else config.YOUTUBE_QUERIES
    for q in queries:
        # search.list cuesta 100 unidades de cuota (el límite diario gratis es 10.000)
        r = requests.get(
            "https://www.googleapis.com/youtube/v3/search",
            params={
                "key": config.YOUTUBE_API_KEY,
                "part": "id",
                "type": "video",
                "q": q,
                "order": "relevance",
                "publishedAfter": _utc_iso(since),
                "maxResults": 25,
            },
            timeout=TIMEOUT,
        )
        if r.status_code != 200:
            print(f"[youtube] error {r.status_code} buscando {q!r}: {r.text[:200]}")
            continue
        for item in r.json().get("items", []):
            vid = item.get("id", {}).get("videoId")
            if vid and vid not in ids:
                ids.append(vid)

    out: list[dict] = []
    # videos.list cuesta 1 unidad por llamada y trae la descripción completa
    for i in range(0, len(ids), 50):
        r = requests.get(
            "https://www.googleapis.com/youtube/v3/videos",
            params={
                "key": config.YOUTUBE_API_KEY,
                "part": "snippet,statistics",
                "id": ",".join(ids[i : i + 50]),
            },
            timeout=TIMEOUT,
        )
        if r.status_code != 200:
            print(f"[youtube] error {r.status_code} en videos.list: {r.text[:200]}")
            continue
        for v in r.json().get("items", []):
            sn, st = v["snippet"], v.get("statistics", {})
            views = int(st.get("viewCount", 0))
            if views < config.YOUTUBE_MIN_VIEWS:
                continue
            out.append(
                {
                    "id": f"yt:{v['id']}",
                    "source": "youtube",
                    "url": f"https://www.youtube.com/watch?v={v['id']}",
                    "video_id": v["id"],
                    "author": sn.get("channelTitle", ""),
                    "published_at": sn.get("publishedAt", ""),
                    "title_original": sn.get("title", ""),
                    "text": (sn.get("description") or "")[:1500],
                    "popularity": views,
                    "thumbnail": (sn.get("thumbnails", {}).get("high") or {}).get("url", ""),
                }
            )
    print(f"[youtube] {len(out)} videos candidatos")
    return out


def fetch_video_details(video_ids: list[str]) -> dict[str, dict]:
    """Descripción y vistas actuales de videos ya conocidos (1 unidad de cuota cada 50)."""
    if not config.YOUTUBE_API_KEY:
        return {}
    out: dict[str, dict] = {}
    for i in range(0, len(video_ids), 50):
        r = requests.get(
            "https://www.googleapis.com/youtube/v3/videos",
            params={
                "key": config.YOUTUBE_API_KEY,
                "part": "snippet,statistics",
                "id": ",".join(video_ids[i : i + 50]),
            },
            timeout=TIMEOUT,
        )
        if r.status_code != 200:
            print(f"[youtube] error {r.status_code} en videos.list: {r.text[:200]}")
            continue
        for v in r.json().get("items", []):
            out[v["id"]] = {
                "description": (v["snippet"].get("description") or "")[:3000],
                "views": int(v.get("statistics", {}).get("viewCount", 0)),
            }
    return out


# ------------------------------------------------------------------ Reddit --

def _reddit_token() -> str | None:
    r = requests.post(
        "https://www.reddit.com/api/v1/access_token",
        auth=(config.REDDIT_CLIENT_ID, config.REDDIT_CLIENT_SECRET),
        data={"grant_type": "client_credentials"},
        headers={"User-Agent": config.REDDIT_USER_AGENT},
        timeout=TIMEOUT,
    )
    if r.status_code != 200:
        print(f"[reddit] no se pudo obtener token: {r.status_code} {r.text[:200]}")
        return None
    return r.json().get("access_token")


def collect_reddit() -> list[dict]:
    if not (config.REDDIT_CLIENT_ID and config.REDDIT_CLIENT_SECRET):
        print("[reddit] sin credenciales, se saltea")
        return []
    token = _reddit_token()
    if not token:
        return []
    headers = {"Authorization": f"bearer {token}", "User-Agent": config.REDDIT_USER_AGENT}
    kw = re.compile("|".join(re.escape(k) for k in config.REDDIT_KEYWORDS), re.I)

    seen: set[str] = set()
    out: list[dict] = []
    for sub in config.SUBREDDITS:
        for listing, extra in (("top", {"t": "day"}), ("hot", {})):
            r = requests.get(
                f"https://oauth.reddit.com/r/{sub}/{listing}",
                params={"limit": 100, **extra},
                headers=headers,
                timeout=TIMEOUT,
            )
            if r.status_code != 200:
                print(f"[reddit] error {r.status_code} en r/{sub}/{listing}")
                continue
            for child in r.json().get("data", {}).get("children", []):
                p = child["data"]
                if p["id"] in seen or p.get("stickied") or p.get("over_18"):
                    continue
                seen.add(p["id"])
                if p.get("score", 0) < config.REDDIT_MIN_SCORE:
                    continue
                blob = f"{p.get('title', '')} {p.get('selftext', '')} {p.get('link_flair_text') or ''}"
                if not kw.search(blob):
                    continue
                created = datetime.fromtimestamp(p["created_utc"], tz=timezone.utc)
                yt = re.search(r"(?:youtube\.com/watch\?v=|youtu\.be/)([\w-]{11})", p.get("url", ""))
                out.append(
                    {
                        "id": f"rd:{p['id']}",
                        "source": "reddit",
                        "url": f"https://www.reddit.com{p['permalink']}",
                        "video_id": yt.group(1) if yt else "",
                        "author": f"u/{p.get('author', '')} · r/{sub}",
                        "published_at": _utc_iso(created),
                        "title_original": p.get("title", ""),
                        "text": (p.get("selftext") or "")[:1500],
                        "popularity": int(p.get("score", 0)),
                        "thumbnail": _reddit_thumb(p),
                    }
                )
    print(f"[reddit] {len(out)} posts candidatos")
    return out


def _reddit_thumb(p: dict) -> str:
    try:
        return p["preview"]["images"][0]["source"]["url"].replace("&amp;", "&")
    except (KeyError, IndexError, TypeError):
        t = p.get("thumbnail", "")
        return t if t.startswith("http") else ""
