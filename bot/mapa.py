"""Mapa esquemático de Leonida hecho por WastedMap.

Silueta simplificada y redibujada a mano (unos pocos puntos de control), con estilo propio:
no es el mapa oficial del juego ni una copia de su arte. Las posiciones son aproximadas:
cada burbuja agrupa los descubrimientos del área.
Todo el dibujo (costa, relieve, rutas) se genera acá en SVG, de forma determinística.
"""
from __future__ import annotations

import math
import random
from html import escape


def P(u: float, v: float) -> tuple[float, float]:
    """Pasa coordenadas de la grilla de referencia (0-780 x 0-1068) al viewBox 0 0 800 900."""
    return 400 + (u - 432) * .95, 45 + (v - 90) * .95


def _xy(u, v):
    x, y = P(u, v)
    return round(x), round(y)


# Área -> (x, y, color, descripción corta).
AREAS = {
    "Port Gellhorn": (*_xy(232, 380), "#ff8a3d", "Puerto industrial del oeste"),
    "Mount Kalaga": (*_xy(385, 235), "#4ade80", "Parque nacional y montañas del norte"),
    "Ambrosia": (*_xy(430, 385), "#ffd54a", "Pueblos del interior y refinería"),
    "Grassrivers": (*_xy(335, 690), "#2ee6d6", "Pantanos y ríos del sur"),
    "Vice City": (*_xy(515, 555), "#ff3d8b", "La gran ciudad de la costa este"),
    "Leonida Keys": (*_xy(250, 905), "#a78bfa", "Cadena de cayos e islas"),
    "Vice Beach": (*_xy(660, 520), "#38bdf8", "Playas e islas frente a Vice City"),
    "Hamlet": (*_xy(440, 735), "#a3e635", "Pueblo del sur, camino a los cayos"),
    "Capri": (*_xy(225, 563), "#f87171", "Pueblo costero del oeste"),
}
# Áreas con el nombre a la izquierda de la burbuja (para que no se pisen con las vecinas).
_LABEL_LEFT: set[str] = set()

# Silueta simplificada de la isla principal (sentido horario desde el noroeste).
_COAST = [
    (262, 215), (290, 160), (330, 128), (375, 112), (420, 118), (450, 108), (485, 118), (512, 150),
    (528, 200), (548, 238), (578, 272), (600, 305), (610, 345), (612, 385), (604, 425), (585, 468),
    (562, 500), (566, 540), (590, 578), (600, 612), (582, 652), (562, 690), (545, 725), (528, 762),
    (505, 792), (476, 818), (444, 832), (410, 838), (372, 828), (334, 806), (300, 776), (268, 742),
    (250, 702), (228, 668), (214, 636), (204, 598), (200, 560), (194, 515), (190, 470), (198, 430),
    (210, 398), (226, 365), (234, 330), (246, 298), (252, 258),
]
# Islas sueltas: (u, v, rx, ry, rotación).
_ISLANDS = [
    (198, 322, 28, 16, .2),                                        # isla del oeste del puerto
    (214, 268, 16, 8, -.5),
    (122, 362, 10, 18, .3), (108, 420, 8, 15, 0), (150, 470, 9, 13, -.3), (138, 562, 8, 16, .4),
    (160, 600, 6, 10, 0),
    (470, 98, 14, 7, 0), (512, 140, 16, 9, .4), (600, 262, 10, 20, .3),   # norte y noreste
    (232, 905, 42, 26, 0),                                         # isla grande del suroeste
    (470, 845, 14, 5, -.9), (452, 872, 16, 5, -.8), (430, 898, 18, 5, -.6), (398, 918, 18, 5, -.3),
    (360, 928, 18, 5, -.1), (322, 932, 16, 5, 0), (178, 885, 12, 6, 0),
]
_BEACH = [(662, 520, 22, 82, -.12), (622, 640, 14, 22, 0), (604, 702, 9, 16, .3)]


def _rough(points, seed, depth=3, amount=0.11):
    """Desplaza puntos medios al azar (con semilla fija) para que el borde parezca una costa real."""
    rnd = random.Random(seed)
    pts = list(points)
    for level in range(depth):
        out = []
        for i, (x1, y1) in enumerate(pts):
            x2, y2 = pts[(i + 1) % len(pts)]
            dx, dy = x2 - x1, y2 - y1
            length = math.hypot(dx, dy) or 1
            off = rnd.uniform(-1, 1) * length * amount / (level + 1) ** 0.5
            out += [(x1, y1), ((x1 + x2) / 2 - dy / length * off, (y1 + y2) / 2 + dx / length * off)]
        pts = out
    return pts


def _path(points) -> str:
    return "M" + " L".join(f"{x:.1f} {y:.1f}" for x, y in points) + " Z"


def _blob(cx, cy, rx, ry, seed, n=14, amount=0.18, rot=0.0):
    c, s = math.cos(rot), math.sin(rot)
    pts = [(cx + rx * math.cos(a) * c - ry * math.sin(a) * s, cy + rx * math.cos(a) * s + ry * math.sin(a) * c)
           for a in (i * 2 * math.pi / n for i in range(n))]
    return _path(_rough(pts, seed, depth=2, amount=amount))


def _isle(u, v, rx, ry, rot, seed):
    return f'<path d="{_blob(*P(u, v), rx * .95, ry * .95, seed=seed, n=12, amount=.16, rot=rot)}"/>'


LAND = _path(_rough([P(*p) for p in _COAST], seed=7, depth=3, amount=.09))
LAKE = _blob(*P(490, 352), 40, 34, seed=3)
KEYS = "".join(_isle(*i, seed=20 + n) for n, i in enumerate(_ISLANDS))
BARRIER = "".join(_isle(*i, seed=60 + n) for n, i in enumerate(_BEACH))


def _around(name, n, sx, sy, seed):
    x0, y0 = AREAS[name][:2]
    rnd = random.Random(seed)
    return [(x0 + rnd.uniform(-sx, sx), y0 + rnd.uniform(-sy, sy)) for _ in range(n)]


def _mountains() -> str:
    rnd = random.Random(11)
    peaks = sorted(((x, y, rnd.uniform(11, 20)) for x, y in _around("Mount Kalaga", 18, 95, 55, 12)),
                   key=lambda p: p[1])  # las de atrás primero
    out = []
    for x, y, s in peaks:
        out.append(f'<path d="M{x - s:.0f} {y:.0f} L{x:.0f} {y - s * 1.2:.0f} L{x + s:.0f} {y:.0f} Z"/>'
                   f'<path class="snow" d="M{x - s * .32:.0f} {y - s * .82:.0f} L{x:.0f} {y - s * 1.2:.0f} L{x + s * .32:.0f} {y - s * .82:.0f} Z"/>')
    return "".join(out)


def _swamp() -> str:
    return "".join(f'<path d="M{x:.0f} {y:.0f} l-4 -8 M{x:.0f} {y:.0f} l0 -10 M{x:.0f} {y:.0f} l4 -8"/>'
                   for x, y in _around("Grassrivers", 55, 85, 75, 5))


def _fields() -> str:
    rnd = random.Random(9)
    out = []
    for x, y in _around("Ambrosia", 22, 90, 60, 9):
        w, h = rnd.uniform(14, 26), rnd.uniform(9, 17)
        out.append(f'<rect x="{x:.0f}" y="{y:.0f}" width="{w:.0f}" height="{h:.0f}" transform="rotate(-12 {x:.0f} {y:.0f})"/>')
    return "".join(out)


def _city() -> str:
    cx, cy = AREAS["Vice City"][:2]
    rnd = random.Random(13)
    out = []
    for i in range(-6, 6):
        for j in range(-7, 7):
            x, y = cx + i * 12, cy + j * 12
            if (i / 6) ** 2 + (j / 7) ** 2 > 1 or rnd.random() < .18:
                continue
            out.append(f'<rect x="{x}" y="{y}" width="9" height="9" rx="1.5" opacity="{rnd.uniform(.35, .9):.2f}"/>')
    return "".join(out)


def _curve(*pts) -> str:
    """Curva suave (Catmull-Rom) que pasa por los puntos dados."""
    d = f"M{pts[0][0]:.0f} {pts[0][1]:.0f}"
    for i in range(len(pts) - 1):
        p0, p1, p2 = pts[max(i - 1, 0)], pts[i], pts[i + 1]
        p3 = pts[min(i + 2, len(pts) - 1)]
        c1 = (p1[0] + (p2[0] - p0[0]) / 6, p1[1] + (p2[1] - p0[1]) / 6)
        c2 = (p2[0] - (p3[0] - p1[0]) / 6, p2[1] - (p3[1] - p1[1]) / 6)
        d += f" C{c1[0]:.0f} {c1[1]:.0f} {c2[0]:.0f} {c2[1]:.0f} {p2[0]:.0f} {p2[1]:.0f}"
    return d


def _rivers() -> str:
    return "".join(f'<path d="{_curve(*[P(*p) for p in r])}"/>' for r in (
        [(470, 390), (440, 450), (400, 500), (370, 560)],
        [(330, 610), (350, 660), (320, 720), (300, 770)],
        [(270, 640), (300, 690), (360, 740), (400, 800)],
        [(560, 300), (530, 330)],
    ))


def _roads() -> str:
    a = {k: v[:2] for k, v in AREAS.items()}
    north_south = _curve(P(430, 160), a["Mount Kalaga"], P(430, 300), a["Ambrosia"], P(432, 470),
                         P(430, 560), P(450, 680), P(450, 760))
    east_west = _curve(a["Port Gellhorn"], P(300, 470), P(400, 540), a["Vice City"])
    south = _curve(P(450, 760), P(470, 820), P(440, 880), P(380, 922), P(300, 932), a["Leonida Keys"])
    branch = _curve(P(432, 600), P(380, 650), a["Grassrivers"])
    north = _curve(a["Port Gellhorn"], P(280, 280), a["Mount Kalaga"], P(500, 240), P(560, 320), P(560, 430), a["Vice City"])
    return "".join(f'<path d="{d}"/>' for d in (north_south, east_west, south, branch, north))


def _compass(x: int, y: int) -> str:
    return (f'<g class="rose" transform="translate({x} {y})">'
            '<circle r="34" class="ring"/><circle r="24" class="ring"/>'
            '<path d="M0 -42 L7 0 L0 6 L-7 0 Z" class="n"/><path d="M0 42 L7 0 L0 -6 L-7 0 Z"/>'
            '<path d="M-42 0 L0 -6 L6 0 L0 6 Z"/><path d="M42 0 L0 -6 L-6 0 L0 6 Z"/>'
            '<text y="-50" text-anchor="middle">N</text></g>')


def map_svg(counts: dict[str, int], links: dict[str, str], root: str) -> str:
    """SVG del mapa con una burbuja por área (tamaño según cantidad de secretos)."""
    tints = []
    grads = []
    for i, (name, (x, y, color, _)) in enumerate(AREAS.items()):
        grads.append(f'<radialGradient id="lm-t{i}"><stop offset="0" stop-color="{color}" stop-opacity=".30"/>'
                     f'<stop offset="1" stop-color="{color}" stop-opacity="0"/></radialGradient>')
        tints.append(f'<circle cx="{x}" cy="{y}" r="190" fill="url(#lm-t{i})"/>')
    bubbles = []
    for name, (x, y, color, desc) in AREAS.items():
        n = counts.get(name, 0)
        r = min(24 + 4.5 * math.sqrt(n), 58) if n else 20
        label = f"{n} secreto{'s' if n != 1 else ''}" if n else "Pronto"
        inner = (f'<circle cx="{x}" cy="{y}" r="{r + 10:.0f}" fill="none" stroke="{color}" stroke-width="3" class="pulse"/>'
                 f'<circle cx="{x}" cy="{y}" r="{r + 16:.0f}" fill="{color}" opacity=".16" class="halo"/>'
                 f'<circle cx="{x}" cy="{y + 4}" r="{r:.0f}" fill="#000" opacity=".35"/>'
                 f'<circle cx="{x}" cy="{y}" r="{r:.0f}" fill="{color}" fill-opacity="{1 if n else .28}" '
                 f'stroke="#fff" stroke-opacity=".9" stroke-width="2.5"/>'
                 f'<circle cx="{x}" cy="{y}" r="{r:.0f}" fill="url(#lm-shine)"/>'
                 f'<text x="{x}" y="{y + 9}" text-anchor="middle" class="num">{n if n else "?"}</text>'
                 + (f'<text x="{x - r - 14:.0f}" y="{y + 2}" text-anchor="end" class="lbl">{escape(name.upper())}</text>'
                    f'<text x="{x - r - 14:.0f}" y="{y + 22}" text-anchor="end" class="sub">{label}</text>'
                    if name in _LABEL_LEFT else
                    f'<text x="{x}" y="{y + r + 30:.0f}" text-anchor="middle" class="lbl">{escape(name.upper())}</text>'
                    f'<text x="{x}" y="{y + r + 50:.0f}" text-anchor="middle" class="sub">{label}</text>'))
        if n and name in links:
            bubbles.append(f'<a href="{root}{links[name]}" aria-label="{escape(name)}: {label}">'
                           f'<g class="area">{inner}</g></a>')
        else:
            bubbles.append(f'<g class="area{"" if n else " off"}">{inner}</g>')
    return f"""<svg class="leonida" viewBox="0 0 800 900" role="img" aria-label="Mapa esquemático de Leonida con los secretos por zona">
<defs>
<radialGradient id="lm-sea" cx=".55" cy=".45" r=".8"><stop offset="0" stop-color="#1b1236"/><stop offset="1" stop-color="#08060f"/></radialGradient>
<linearGradient id="lm-land" x1="0" y1="0" x2=".6" y2="1"><stop offset="0" stop-color="#2d1a48"/><stop offset="1" stop-color="#1a1030"/></linearGradient>
<radialGradient id="lm-shine" cx=".35" cy=".3" r=".7"><stop offset="0" stop-color="#fff" stop-opacity=".45"/><stop offset=".5" stop-color="#fff" stop-opacity="0"/></radialGradient>
{"".join(grads)}
<pattern id="lm-waves" width="44" height="22" patternUnits="userSpaceOnUse"><path d="M2 14 q9 -8 18 0 t18 0" fill="none" stroke="#2ee6d6" stroke-opacity=".07" stroke-width="1.5"/></pattern>
<clipPath id="lm-clip"><path d="{LAND}"/></clipPath>
<filter id="lm-glow" x="-10%" y="-10%" width="120%" height="120%"><feGaussianBlur stdDeviation="5" result="b"/><feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge></filter>
<filter id="lm-blur"><feGaussianBlur stdDeviation="9"/></filter>
</defs>
<rect width="800" height="900" fill="url(#lm-sea)"/>
<rect width="800" height="900" fill="url(#lm-waves)"/>
<g fill="none" stroke="#fff" stroke-opacity=".04">{"".join(f'<path d="M{x} 0V900"/>' for x in range(100, 800, 100))}{"".join(f'<path d="M0 {y}H800"/>' for y in range(100, 900, 100))}</g>
<text x="40" y="250" class="sea">GOLFO</text><text x="782" y="250" class="sea" transform="rotate(90 782 250)">OCÉANO</text>
<path d="{LAND}" fill="none" stroke="#2ee6d6" stroke-opacity=".22" stroke-width="26" filter="url(#lm-blur)"/>
<g fill="#2ee6d6" fill-opacity=".12" filter="url(#lm-blur)">{KEYS}</g>
<path d="{LAND}" fill="url(#lm-land)"/>
<g clip-path="url(#lm-clip)">
{"".join(tints)}
<g class="fields">{_fields()}</g>
<g class="swamp">{_swamp()}</g>
<g class="rivers">{_rivers()}</g>
<path d="{LAKE}" class="lake"/>
<g class="mts">{_mountains()}</g>
<g class="city">{_city()}</g>
<path d="M{AREAS['Port Gellhorn'][0] - 30} {AREAS['Port Gellhorn'][1] + 22} v26 m30 2 v26 m30 -2 v24" class="docks"/>
</g>
<g class="roads">{_roads()}</g>
<path d="{LAND}" fill="none" stroke="#ff3d8b" stroke-width="2.5" stroke-opacity=".85" stroke-linejoin="round" filter="url(#lm-glow)"/>
<g fill="url(#lm-land)" stroke="#ff3d8b" stroke-width="1.8" stroke-opacity=".75">{KEYS}{BARRIER}</g>
{_compass(90, 680)}
<g class="cartouche" transform="translate(530 800)"><rect width="230" height="66" rx="10"/>
<text x="16" y="30" class="t1">LEONIDA</text><text x="16" y="50" class="t2">Mapa esquemático · WastedMap</text></g>
{"".join(bubbles)}
</svg>"""
