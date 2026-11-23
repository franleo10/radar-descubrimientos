"""Configuración del bot. Todo se puede pisar con variables de entorno."""
import os
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DOCS_DIR = ROOT / "docs"          # lo que se publica (GitHub Pages)
DATA_FILE = DOCS_DIR / "data.json"
STATE_FILE = ROOT / "state" / "seen.json"  # ids ya procesados, para no pagar dos veces


def _load_dotenv() -> None:
    """Carga un .env local si existe (en GitHub Actions se usan los Secrets)."""
    env = ROOT / ".env"
    if not env.exists():
        return
    for line in env.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        k, v = line.split("=", 1)
        os.environ.setdefault(k.strip(), v.strip().strip('"').strip("'"))


_load_dotenv()


def _list(name: str, default: str) -> list[str]:
    return [x.strip() for x in os.environ.get(name, default).split("|") if x.strip()]


# --- Claves (nunca van en el código) ---
YOUTUBE_API_KEY = os.environ.get("YOUTUBE_API_KEY", "")
REDDIT_CLIENT_ID = os.environ.get("REDDIT_CLIENT_ID", "")
REDDIT_CLIENT_SECRET = os.environ.get("REDDIT_CLIENT_SECRET", "")
REDDIT_USER_AGENT = os.environ.get("REDDIT_USER_AGENT", "script:discoveries-bot:v0.1")

# --- Qué buscar ---
YOUTUBE_QUERIES = _list(
    "YOUTUBE_QUERIES",
    "GTA 6 easter egg|GTA 6 secret location|GTA 6 hidden|GTA 6 ubicación secreta|"
    "GTA 6 secreto|GTA 6 how to get|GTA 6 rare car|GTA 6 money guide",
)
YOUTUBE_MIN_VIEWS = int(os.environ.get("YOUTUBE_MIN_VIEWS", "2000"))
YOUTUBE_LOOKBACK_HOURS = int(os.environ.get("YOUTUBE_LOOKBACK_HOURS", "24"))

SUBREDDITS = _list("SUBREDDITS", "GTA6|GTAVI")
REDDIT_MIN_SCORE = int(os.environ.get("REDDIT_MIN_SCORE", "50"))
# Filtro barato antes de llamar a Claude: el post tiene que mencionar alguna de estas.
REDDIT_KEYWORDS = _list(
    "REDDIT_KEYWORDS",
    "easter egg|secret|hidden|found|location|where to|how to get|collectible|rare|"
    "glitch|money|guide|tip|secreto|ubicación|encontré",
)

# --- Claude ---
CLAUDE_MODEL = os.environ.get("CLAUDE_MODEL", "claude-haiku-5-5")
CLAUDE_BATCH_SIZE = int(os.environ.get("CLAUDE_BATCH_SIZE", "15"))
# Cuántos descubrimientos ya publicados se amplían (guía, pasos, región) por corrida.
ENRICH_PER_RUN = int(os.environ.get("ENRICH_PER_RUN", "40"))

# --- Redes (cada una se saltea si no tiene claves) ---
TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN", "")
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID", "")  # ej. @wastedmap
BLUESKY_HANDLE = os.environ.get("BLUESKY_HANDLE", "")
BLUESKY_APP_PASSWORD = os.environ.get("BLUESKY_APP_PASSWORD", "")
SOCIAL_PER_RUN = int(os.environ.get("SOCIAL_PER_RUN", "3"))  # por red y por corrida
SOCIAL_MAX_AGE_DAYS = int(os.environ.get("SOCIAL_MAX_AGE_DAYS", "3"))

# --- Web ---
SITE_NAME = os.environ.get("SITE_NAME", "WastedMap")
# Dirección pública de la web, sin "/" al final. Cambiala cuando tengas dominio propio.
SITE_URL = (os.environ.get("SITE_URL") or "https://wastedmap.com").rstrip("/")
# Clave PÚBLICA del widget de Turnstile (la secreta va solo en Cloudflare).
TURNSTILE_SITEKEY = os.environ.get("TURNSTILE_SITEKEY") or "0x4AAAAAAGPi3Jn1ITCgmyhh"
MAX_ENTRIES = int(os.environ.get("MAX_ENTRIES", "600"))
