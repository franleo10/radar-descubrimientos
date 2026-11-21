# Radar de Descubrimientos (bot de GTA 6)

Cada 6 horas, el bot:

1. Busca videos nuevos en YouTube y posts en Reddit (r/GTA6, r/GTAVI) usando sus **APIs oficiales**.
2. Le pasa los candidatos a Claude, que descarta lo que no sirve (noticias, memes, quejas) y escribe en español un título, un resumen, la zona y cómo conseguirlo.
3. Guarda todo en `docs/data.json`, y la web (`docs/index.html`) lo muestra con el video original insertado.

Corre gratis en GitHub Actions y se publica gratis en GitHub Pages. Tu PC no tiene que estar prendida.

## Lo que tenés que hacer una sola vez

### 1. Sacar las claves (todas gratis, salvo Claude)

| Clave | Dónde |
|---|---|
| `ANTHROPIC_API_KEY` | console.anthropic.com → API Keys (necesita crédito cargado) |
| `YOUTUBE_API_KEY` | console.cloud.google.com → crear proyecto → habilitar "YouTube Data API v3" → Credenciales → Clave de API |
| `REDDIT_CLIENT_ID`, `REDDIT_CLIENT_SECRET`, `REDDIT_USER_AGENT` | **Opcionales.** Reddit exige aprobación previa para usar su API (reddit.com/wiki/api → "submit a request"). Sin estas claves, el bot funciona solo con YouTube. Si te aprueban: reddit.com/prefs/apps → app tipo **script**; el User-Agent es `script:discoveries-bot:v0.1 (by /u/TU_USUARIO)` |

### 2. Subirlo a GitHub

1. Creá un repositorio nuevo (puede ser público, porque las claves no van en el código).
2. Subí esta carpeta.
3. En **Settings → Secrets and variables → Actions**, cargá las claves de arriba (las de Reddit solo si te aprobaron) con esos mismos nombres.
4. En **Settings → Pages**, elegí *Deploy from a branch*, rama `main`, carpeta `/docs`.
5. En **Actions → Bot de descubrimientos → Run workflow** podés correrlo por primera vez sin esperar.

Listo. La web queda en `https://TU_USUARIO.github.io/NOMBRE_DEL_REPO/`.

## Probar en tu PC

```bash
pip install -r requirements.txt
python -m bot.main --demo        # datos de ejemplo, sin claves
python -m http.server -d docs 8000   # y abrí http://localhost:8000
```

Para una corrida real en tu PC, copiá `.env.example` como `.env` y completalo.

## Ajustes (variables de entorno opcionales)

- `YOUTUBE_QUERIES`: búsquedas separadas con `|`.
- `YOUTUBE_MIN_VIEWS` (2000) y `REDDIT_MIN_SCORE` (50): popularidad mínima para tener en cuenta algo.
- `SUBREDDITS`: por defecto `GTA6|GTAVI`.
- `CLAUDE_MODEL`: por defecto `claude-opus-5-5`. Si querés gastar menos, probá `claude-haiku-5-5`.
- `SITE_NAME`: el nombre que aparece en la web.

## Costos estimados

- GitHub Actions y Pages: gratis.
- YouTube: 8 búsquedas × 4 corridas = ~3.300 unidades por día, de un límite gratis de 10.000.
- Reddit: gratis para este uso.
- Claude: cada candidato se analiza una sola vez (`state/seen.json` guarda los ya vistos), en tandas de 15. Con un par de cientos de candidatos por día, son pocos dólares por mes.

## Reglas que respeta

- No descarga videos: los muestra con el reproductor oficial de YouTube, así las vistas son del creador.
- No usa el logo, el arte ni el nombre de la marca como nombre del sitio, y aclara que es una guía no oficial.
- Descarta trucos para duplicar dinero, venta de cuentas y contenido +18.
