"""Mapa esquemático propio de Leonida (no usa ni calca el mapa oficial del juego).

Es una península simplificada con las grandes áreas que mostraron los tráilers.
Las posiciones son aproximadas: cada burbuja agrupa los descubrimientos del área.
"""
from __future__ import annotations

import math
from html import escape

# Área -> (x, y, color, descripción corta). Coordenadas del viewBox 0 0 800 900.
AREAS = {
    "Port Gellhorn": (205, 190, "#ff8a3d", "Puerto industrial del oeste"),
    "Mount Kalaga": (560, 180, "#4ade80", "Parque nacional y montañas del norte"),
    "Ambrosia": (500, 390, "#ffd54a", "Pueblos del interior y refinería"),
    "Grassrivers": (520, 640, "#2ee6d6", "Pantanos y ríos del sur"),
    "Vice City": (680, 620, "#ff3d8b", "La gran ciudad de la costa este"),
    "Leonida Keys": (430, 790, "#a78bfa", "Cadena de cayos e islas"),
}

LAND = ("M58 128 C140 118 260 122 380 112 C430 108 470 120 520 110 L640 100 C690 96 712 124 702 168 "
        "L690 300 C684 380 706 450 724 520 C744 600 740 680 694 742 C664 782 612 794 586 762 "
        "C562 732 542 694 522 652 C500 608 472 560 452 502 C432 452 418 402 398 362 "
        "C378 322 338 292 298 272 C248 252 198 246 150 252 C108 256 72 252 56 222 C44 196 44 150 58 128 Z")

KEYS = [(560, 800, 26, 9), (520, 822, 22, 8), (478, 838, 24, 8), (432, 850, 20, 7),
        (388, 858, 22, 7), (344, 862, 18, 6), (304, 864, 14, 5)]


def map_svg(counts: dict[str, int], links: dict[str, str], root: str) -> str:
    """SVG del mapa con una burbuja por área (tamaño según cantidad de secretos)."""
    grid = "".join(f'<line x1="{x}" y1="0" x2="{x}" y2="900"/>' for x in range(0, 801, 50)) + \
           "".join(f'<line x1="0" y1="{y}" x2="800" y2="{y}"/>' for y in range(0, 901, 50))
    keys = "".join(f'<ellipse cx="{x}" cy="{y}" rx="{rx}" ry="{ry}"/>' for x, y, rx, ry in KEYS)
    bubbles = []
    for name, (x, y, color, desc) in AREAS.items():
        n = counts.get(name, 0)
        r = min(24 + 4.5 * math.sqrt(n), 58) if n else 20
        label = f"{n} secreto{'s' if n != 1 else ''}" if n else "Pronto"
        inner = (f'<circle cx="{x}" cy="{y}" r="{r + 14:.0f}" fill="{color}" opacity=".14" class="halo"/>'
                 f'<circle cx="{x}" cy="{y}" r="{r:.0f}" fill="{color}" fill-opacity="{.9 if n else .25}" '
                 f'stroke="#fff" stroke-opacity=".85" stroke-width="2"/>'
                 f'<text x="{x}" y="{y + 9}" text-anchor="middle" class="num">{n if n else "?"}</text>'
                 f'<text x="{x}" y="{y + r + 30:.0f}" text-anchor="middle" class="lbl">{escape(name.upper())}</text>'
                 f'<text x="{x}" y="{y + r + 50:.0f}" text-anchor="middle" class="sub">{label}</text>')
        if n and name in links:
            bubbles.append(f'<a href="{root}{links[name]}" aria-label="{escape(name)}: {label}">'
                           f'<g class="area">{inner}</g></a>')
        else:
            bubbles.append(f'<g class="area off">{inner}</g>')
    return f"""<svg class="leonida" viewBox="0 0 800 900" role="img" aria-label="Mapa esquemático de Leonida con los secretos por zona">
<defs>
<linearGradient id="sea" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#140d26"/><stop offset="1" stop-color="#0b0912"/></linearGradient>
<linearGradient id="land" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#2a1640"/><stop offset="1" stop-color="#1c1030"/></linearGradient>
<filter id="glow" x="-20%" y="-20%" width="140%" height="140%"><feGaussianBlur stdDeviation="6" result="b"/><feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge></filter>
</defs>
<rect width="800" height="900" fill="url(#sea)"/>
<g stroke="#ff3d8b" stroke-opacity=".07">{grid}</g>
<path d="{LAND}" fill="url(#land)" stroke="#ff3d8b" stroke-width="3" stroke-opacity=".8" filter="url(#glow)"/>
<g fill="url(#land)" stroke="#ff3d8b" stroke-width="2" stroke-opacity=".7">{keys}</g>
<ellipse cx="610" cy="505" rx="30" ry="22" fill="#140d26" stroke="#2ee6d6" stroke-opacity=".5" stroke-width="2"/>
<text x="740" y="60" text-anchor="end" class="compass">N ↑</text>
{"".join(bubbles)}
</svg>"""
