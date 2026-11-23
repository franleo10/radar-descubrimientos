"""Genera docs/hero.svg: atardecer retro con sol, palmeras, ciudad y grilla (diseño propio).

Uso: python tools/make_hero.py
"""
import math
import random
from pathlib import Path

W, H, HORIZON = 1440, 560, 380
random.seed(11)


def palm(x, y, scale, flip=False):
    """Palmera en silueta con tronco curvo y hojas caídas."""
    s = -1 if flip else 1
    tx, ty = 34 * s, -270  # copa
    parts = [f'<path d="M{-9*s} 0 C {2*s} -95, {14*s} -190, {tx-4*s} {ty+2} L {tx+6*s} {ty} '
             f'C {24*s} -186, {14*s} -92, {11*s} 0 Z"/>']
    for ang, length, droop in [(-170, 150, 70), (-145, 135, 60), (-115, 105, 30), (-80, 100, 25),
                               (-45, 135, 55), (-15, 150, 75), (10, 120, 85), (190, 110, 80)]:
        a = math.radians(ang)
        ex, ey = tx + s * length * math.cos(a), ty + length * math.sin(a) + droop
        mx, my = tx + s * length * 0.55 * math.cos(a), ty + length * 0.55 * math.sin(a) - 18
        nx, ny = -math.sin(a) * 14, math.cos(a) * 14
        parts.append(f'<path d="M{tx:.1f} {ty:.1f} Q {mx+nx*s:.1f} {my+ny:.1f} {ex:.1f} {ey:.1f} '
                     f'Q {mx-nx*s:.1f} {my-ny+10:.1f} {tx:.1f} {ty:.1f} Z"/>')
    parts.append(f'<circle cx="{tx}" cy="{ty+4}" r="9"/>')
    return f'<g transform="translate({x} {y}) scale({scale})" fill="#07040c">{"".join(parts)}</g>'


BUILDINGS = []


def skyline():
    pts, x = [f"0,{HORIZON}"], 0
    while x < W:
        w = random.randint(26, 64)
        if 260 < x < 780:  # centro de la ciudad: torres altas
            h = random.choice([60, 85, 110, 140, 170, 120, 95])
        else:  # afueras bajas, así se ve el sol
            h = random.choice([10, 16, 22, 30])
        BUILDINGS.append((x, w, h))
        pts += [f"{x},{HORIZON-h:.0f}", f"{x+w},{HORIZON-h:.0f}"]
        x += w + random.randint(0, 6)
    pts.append(f"{W},{HORIZON}")
    return f'<polygon points="{" ".join(pts)}" fill="#14081f"/>'


def windows():
    out = []
    for (x, w, h) in BUILDINGS:
        if h < 60:
            continue
        for wy in range(int(HORIZON - h + 8), HORIZON - 6, 9):
            for wx in range(x + 5, x + w - 5, 8):
                if random.random() < 0.28:
                    out.append(f'<rect x="{wx}" y="{wy}" width="3" height="4" fill="#ffb547" '
                               f'opacity="{random.uniform(.3,.85):.2f}"/>')
    return "".join(out)


def grid():
    lines, vx = [], W / 2
    for i in range(-26, 27):
        x0 = vx + i * 120
        lines.append(f'<line x1="{vx + i*6:.0f}" y1="{HORIZON}" x2="{x0:.0f}" y2="{H}"/>')
    y, step = HORIZON + 4, 5
    while y < H:
        lines.append(f'<line x1="0" y1="{y:.0f}" x2="{W}" y2="{y:.0f}"/>')
        step *= 1.32
        y += step
    return f'<g stroke="#ff3d8b" stroke-width="1.6" opacity=".55">{"".join(lines)}</g>'


def stars():
    return "".join(f'<circle cx="{random.randint(0,W)}" cy="{random.randint(0,HORIZON-150)}" '
                   f'r="{random.choice([0.8,1,1.2,1.6])}" fill="#fff" opacity="{random.uniform(.3,.9):.2f}"/>'
                   for _ in range(90))


sun_cx, sun_cy, sun_r = 1030, HORIZON - 120, 150
bars = "".join(f'<rect x="0" y="{sun_cy + 6 + k*20}" width="{W}" height="{2.5 + k*2.4:.1f}" fill="#000"/>'
               for k in range(0, 8))
svg = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" preserveAspectRatio="xMidYMax slice" role="img" aria-label="Atardecer con palmeras sobre la ciudad">
<defs>
<linearGradient id="sky" x1="0" y1="0" x2="0" y2="1">
<stop offset="0" stop-color="#0d0b14"/><stop offset=".42" stop-color="#2a0b3a"/>
<stop offset=".58" stop-color="#6a1650"/><stop offset=".85" stop-color="#d6336c"/><stop offset="1" stop-color="#ff7a5c"/>
</linearGradient>
<linearGradient id="sun" x1="0" y1="0" x2="0" y2="1">
<stop offset="0" stop-color="#ffe37a"/><stop offset=".55" stop-color="#ff8a4c"/><stop offset="1" stop-color="#ff3d8b"/>
</linearGradient>
<linearGradient id="floor" x1="0" y1="0" x2="0" y2="1">
<stop offset="0" stop-color="#2a0b3a"/><stop offset="1" stop-color="#0d0b14"/>
</linearGradient>
<mask id="sunbars"><rect width="{W}" height="{H}" fill="#fff"/>{bars}</mask>
<radialGradient id="glow"><stop offset="0" stop-color="#ff3d8b" stop-opacity=".55"/><stop offset="1" stop-color="#ff3d8b" stop-opacity="0"/></radialGradient>
</defs>
<rect width="{W}" height="{HORIZON}" fill="url(#sky)"/>
{stars()}
<circle cx="{sun_cx}" cy="{sun_cy}" r="{sun_r*2}" fill="url(#glow)"/>
<circle cx="{sun_cx}" cy="{sun_cy}" r="{sun_r}" fill="url(#sun)" mask="url(#sunbars)"/>
{skyline()}{windows()}
<rect y="{HORIZON}" width="{W}" height="{H-HORIZON}" fill="url(#floor)"/>
{grid()}
<rect y="{HORIZON-1}" width="{W}" height="2" fill="#ff6a5c" opacity=".8"/>
{palm(70, H, 1.25)}{palm(205, H + 10, 0.95)}{palm(1380, H, 1.3, flip=True)}{palm(1265, H + 14, 0.9, flip=True)}
</svg>
'''
out = Path(__file__).resolve().parent.parent / "docs" / "hero.svg"
out.write_text(svg, encoding="utf-8")
print(out, len(svg) // 1024, "KB")
