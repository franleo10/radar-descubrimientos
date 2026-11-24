"""Genera docs/og.png (imagen para compartir, 1200x630) con el diseño actual del sitio.

Arma una página con el mismo sistema visual (papel claro, tinta, rosa de marca y el mapa
en modo noche) y le saca una captura con Chrome sin ventana.

Uso: python tools/make_og.py
"""
import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from bot.mapa import AREAS, map_svg  # noqa: E402

DOCS = ROOT / "docs"


def chrome() -> str:
    for c in (r"C:\Program Files\Google\Chrome\Application\chrome.exe",
              r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
              "google-chrome", "chromium", "chrome"):
        if Path(c).exists() or shutil.which(c):
            return c
    raise SystemExit("No encontré Chrome")


data = json.loads((DOCS / "data.json").read_text(encoding="utf-8"))
counts: dict[str, int] = {}
for e in data["entries"]:
    if e.get("macro") in AREAS:
        counts[e["macro"]] = counts.get(e["macro"], 0) + 1
svg = map_svg(counts, {a: "" for a in AREAS}, "", legend=False)
font = (DOCS / "fonts" / "inter.woff2").as_uri()
pin = ('<svg viewBox="0 0 30 38" width="46" height="58"><path d="M15 1C7.3 1 1 7 1 14.6 1 24.8 15 37 15 37s14-12.2 14-22.4C29 7 22.7 1 15 1z" fill="#d61f69"/>'
       '<path d="M15 7.6l1.9 5.1 5.1 1.9-5.1 1.9-1.9 5.1-1.9-5.1-5.1-1.9 5.1-1.9z" fill="#fff"/></svg>')

css = (DOCS / "site.css").as_uri()
html = f"""<!doctype html><html><head><meta charset="utf-8"><link rel="stylesheet" href="{css}"><style>
*,*::before,*::after{{animation:none!important;transition:none!important}}
@font-face{{font-family:Inter;src:url("{font}") format("woff2");font-weight:100 900}}
*{{box-sizing:border-box;margin:0}}
html,body{{width:1200px;height:630px;overflow:hidden}}
body{{background:#f6f3ee;color:#17131f;font-family:Inter,sans-serif;display:grid;grid-template-columns:640px 1fr;-webkit-font-smoothing:antialiased}}
.l{{padding:58px 0 54px 64px;display:flex;flex-direction:column}}
.logo{{display:flex;align-items:center;gap:14px;font-weight:800;font-size:38px;letter-spacing:-.03em}}
.logo b{{color:#d61f69}}
.logo svg{{width:46px!important;height:58px!important}}
.leonida .num,.leonida .sub,.leonida .sea{{display:none}}
.kick{{margin-top:auto;font:600 15px ui-monospace,Consolas,monospace;letter-spacing:.12em;text-transform:uppercase;color:#6e6779;display:flex;align-items:center;gap:10px}}
.kick i{{width:9px;height:9px;border-radius:50%;background:#d61f69;display:block}}
h1{{margin-top:18px;font-size:68px;line-height:1.02;letter-spacing:-.04em;font-weight:800}}
h1 em{{font-style:normal;color:#d61f69;background:linear-gradient(#d61f69,#d61f69) 0 94%/100% 7px no-repeat}}
.sub{{margin-top:24px;font-size:24px;color:#3d3747;font-weight:500}}
.url{{margin-top:auto;display:inline-flex;align-self:flex-start;background:#17131f;color:#fff;font-weight:700;font-size:22px;padding:13px 24px;border-radius:8px}}
.r{{margin:28px 28px 28px 0;background:#14111c;border-radius:20px;overflow:hidden;position:relative}}
.r svg.leonida{{position:absolute;left:50%;top:50%;width:640px;height:auto;transform:translate(-50%,-47%)}}
.r::after{{content:"";position:absolute;inset:0;background:repeating-radial-gradient(circle at 50% 50%,rgba(255,255,255,.04) 0 1px,transparent 1px 90px);pointer-events:none}}
.r .scan{{position:absolute;left:50%;top:50%;width:900px;height:900px;translate:-50% -50%;border-radius:50%;
  background:conic-gradient(from 210deg,rgba(255,92,147,0) 0deg,rgba(255,92,147,0) 290deg,rgba(255,92,147,.12) 335deg,rgba(255,92,147,.38) 359deg,rgba(255,92,147,0) 360deg);mix-blend-mode:screen}}
</style></head><body>
<div class="l">
  <div class="logo og-logo">{pin}<span>Wasted<b>Map</b></span></div>
  <p class="kick"><i></i>Guía no oficial · Se actualiza cada día</p>
  <h1>Los secretos de GTA&nbsp;6 en <em>un solo mapa</em></h1>
  <p class="sub">Easter eggs, lugares escondidos, autos raros y guías paso a paso.</p>
  <p class="url">wastedmap.com</p>
</div>
<div class="r">{svg}<div class="scan"></div></div>
</body></html>"""

with tempfile.TemporaryDirectory() as tmp:
    page = Path(tmp) / "og.html"
    page.write_text(html, encoding="utf-8")
    out = Path(tmp) / "og.png"
    subprocess.run([chrome(), "--headless=new", "--disable-gpu", "--hide-scrollbars", "--force-device-scale-factor=1",
                    "--window-size=1200,630", f"--screenshot={out}", "--virtual-time-budget=2000", page.as_uri()],
                   check=True, capture_output=True)
    from PIL import Image
    Image.open(out).convert("RGB").save(DOCS / "og.png", optimize=True)
print("listo: docs/og.png")
