"""Genera los íconos PNG y la imagen para compartir de WastedMap (diseño propio).

Uso: python tools/make_brand.py
"""
import random
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageFont

DOCS = Path(__file__).resolve().parent.parent / "docs"
ANTON = str(DOCS / "fonts" / "anton.woff2")
INTER = str(DOCS / "fonts" / "inter.woff2")
PINK, CORAL, ORANGE, BG = (255, 61, 139), (255, 122, 92), (255, 181, 71), (11, 9, 18)


def gradient(size, stops, horizontal=True):
    """Degradé lineal con varios colores."""
    w, h = size
    line = Image.new("RGB", (256, 1))
    px = line.load()
    for i in range(256):
        t = i / 255
        for j in range(len(stops) - 1):
            p0, c0 = stops[j]
            p1, c1 = stops[j + 1]
            if p0 <= t <= p1:
                k = (t - p0) / (p1 - p0 or 1)
                px[i, 0] = tuple(int(c0[n] + (c1[n] - c0[n]) * k) for n in range(3))
                break
    if horizontal:
        return line.resize((w, h), Image.BILINEAR)
    return line.rotate(-90, expand=True).resize((w, h), Image.BILINEAR)


def pin_mask(size, s=4):
    """Pin con agujero y destello de 4 puntas (el isotipo)."""
    w, h = size
    m = Image.new("L", (w * s, h * s), 0)
    d = ImageDraw.Draw(m)
    W_, H_ = w * s, h * s
    cx, r = W_ / 2, W_ * 0.47
    cy = r + H_ * 0.02
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=255)
    d.polygon([(cx - r * 0.88, cy + r * 0.45), (cx + r * 0.88, cy + r * 0.45), (cx, H_ * 0.985)], fill=255)
    hole = r * 0.5
    d.ellipse([cx - hole, cy - hole, cx + hole, cy + hole], fill=0)
    a, b = hole * 0.74, hole * 0.2  # destello
    d.polygon([(cx, cy - a), (cx + b, cy - b), (cx + a, cy), (cx + b, cy + b),
               (cx, cy + a), (cx - b, cy + b), (cx - a, cy), (cx - b, cy - b)], fill=255)
    return m.resize(size, Image.LANCZOS)


def pin(size):
    img = gradient(size, [(0, PINK), (1, ORANGE)]).convert("RGBA")
    img.putalpha(pin_mask(size))
    # el destello va en blanco
    white = Image.new("RGBA", size, (255, 255, 255, 255))
    star = Image.new("L", size, 0)
    sm = pin_mask(size)
    hole_only = Image.new("L", size, 0)
    s = 4
    big = Image.new("L", (size[0] * s, size[1] * s), 0)
    d = ImageDraw.Draw(big)
    W_, H_ = size[0] * s, size[1] * s
    cx, r = W_ / 2, W_ * 0.47
    cy = r + H_ * 0.02
    hole = r * 0.5
    a, b = hole * 0.74, hole * 0.2
    d.polygon([(cx, cy - a), (cx + b, cy - b), (cx + a, cy), (cx + b, cy + b),
               (cx, cy + a), (cx - b, cy + b), (cx - a, cy), (cx - b, cy - b)], fill=255)
    star = big.resize(size, Image.LANCZOS)
    white.putalpha(star)
    img.alpha_composite(white)
    return img


def icon(px):
    s = 4
    base = Image.new("RGBA", (px * s, px * s), (0, 0, 0, 0))
    ImageDraw.Draw(base).rounded_rectangle([0, 0, px * s - 1, px * s - 1], radius=int(px * s * 0.22), fill=BG)
    base = base.resize((px, px), Image.LANCZOS)
    p = pin((int(px * 0.58), int(px * 0.74)))
    base.alpha_composite(p, ((px - p.width) // 2, int(px * 0.12)))
    return base


icon(180).save(DOCS / "apple-touch-icon.png")
icon(32).save(DOCS / "favicon-32.png")
icon(512).save(DOCS / "icon-512.png")

# --- Imagen para compartir (1200x630): atardecer retro + marca ---
W, H, HZ = 1200, 630, 420
random.seed(5)
og = Image.new("RGBA", (W, H), BG + (255,))
sky = gradient((W, HZ), [(0, BG), (.45, (42, 11, 58)), (.75, (106, 22, 80)), (1, (255, 106, 92))], horizontal=False)
og.paste(sky, (0, 0))
d = ImageDraw.Draw(og)
for _ in range(70):
    x, y = random.randint(0, W), random.randint(0, HZ - 160)
    d.ellipse([x, y, x + 2, y + 2], fill=(255, 255, 255, random.randint(80, 220)))
# sol con franjas
sun_c, sun_r = (900, HZ - 70), 175
glow = Image.new("L", (W, H), 0)
ImageDraw.Draw(glow).ellipse([sun_c[0] - sun_r - 70, sun_c[1] - sun_r - 70, sun_c[0] + sun_r + 70, sun_c[1] + sun_r + 70], fill=140)
glow = glow.filter(ImageFilter.GaussianBlur(60))
og.alpha_composite(Image.merge("RGBA", (*Image.new("RGB", (W, H), PINK).split(), glow)))
sun_mask = Image.new("L", (W, H), 0)
sd = ImageDraw.Draw(sun_mask)
sd.ellipse([sun_c[0] - sun_r, sun_c[1] - sun_r, sun_c[0] + sun_r, sun_c[1] + sun_r], fill=255)
for k in range(8):
    y = sun_c[1] + 10 + k * 21
    sd.rectangle([0, y, W, y + 3 + k * 2.4], fill=0)
sun = gradient((W, H), [(0, (255, 227, 122)), (.62, (255, 138, 76)), (.78, PINK), (1, PINK)], horizontal=False)
og.alpha_composite(Image.merge("RGBA", (*sun.split(), sun_mask)))
# ciudad
x = 0
while x < W:
    w = random.randint(24, 60)
    h = random.choice([60, 90, 120, 150, 110]) if 560 < x < 1000 else random.choice([12, 18, 26])
    d.rectangle([x, HZ - h, x + w, HZ], fill=(20, 8, 31))
    x += w + random.randint(0, 5)
# piso con grilla
floor = gradient((W, H - HZ), [(0, (42, 11, 58)), (1, BG)], horizontal=False)
og.paste(floor, (0, HZ))
grid = Image.new("RGBA", (W, H), (0, 0, 0, 0))
gd = ImageDraw.Draw(grid)
vx = W * 0.72
for i in range(-30, 31):
    gd.line([(vx + i * 5, HZ), (vx + i * 110, H)], fill=(255, 61, 139, 120), width=2)
y, step = HZ + 4, 5
while y < H:
    gd.line([(0, y), (W, y)], fill=(255, 61, 139, 120), width=2)
    step *= 1.35
    y += step
og.alpha_composite(grid)
d = ImageDraw.Draw(og)
d.rectangle([0, HZ - 1, W, HZ + 1], fill=(255, 106, 92))
# velo oscuro a la izquierda para leer el texto
veil = gradient((W, H), [(0, (11, 9, 18)), (.55, (11, 9, 18)), (1, (11, 9, 18))])
va = gradient((W, H), [(0, (235, 235, 235)), (.45, (190, 190, 190)), (.75, (0, 0, 0)), (1, (0, 0, 0))]).convert("L")
og.alpha_composite(Image.merge("RGBA", (*veil.split(), va)))

# marca: isotipo + WASTEDMAP inclinado
p = pin((92, 118))
og.alpha_composite(p, (64, 60))
title = ImageFont.truetype(ANTON, 104)
layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
ld = ImageDraw.Draw(layer)
ld.text((180, 58), "WASTED", font=title, fill=(255, 255, 255, 255))
wbox = ld.textbbox((180, 58), "WASTED", font=title)
mask = Image.new("L", (W, H), 0)
ImageDraw.Draw(mask).text((wbox[2] + 4, 58), "MAP", font=title, fill=255)
mbox = ImageDraw.Draw(mask).textbbox((wbox[2] + 4, 58), "MAP", font=title)
grad = Image.new("RGB", (W, H), ORANGE)
grad.paste(gradient((mbox[2] - mbox[0] + 4, 140), [(0, PINK), (.55, CORAL), (1, ORANGE)]), (mbox[0], 58))
layer.alpha_composite(Image.merge("RGBA", (*grad.split(), mask)))
layer = layer.transform((W, H), Image.AFFINE, (1, 0.14, -0.14 * 120, 0, 1, 0), resample=Image.BICUBIC)
og.alpha_composite(layer)

d = ImageDraw.Draw(og)
head = ImageFont.truetype(ANTON, 58)
d.text((66, 238), "TODOS LOS SECRETOS", font=head, fill=(255, 255, 255))
d.text((66, 304), "DE GTA 6 EN UN SOLO MAPA", font=head, fill=(255, 255, 255))
body = ImageFont.truetype(INTER, 27)
body.set_variation_by_axes([500]) if hasattr(body, "set_variation_by_axes") else None
d.text((68, 392), "Easter eggs · Lugares secretos · Autos · Guías", font=body, fill=(207, 198, 224))
pill = ImageFont.truetype(INTER, 26)
try:
    pill.set_variation_by_axes([800])
except Exception:
    pass
bx = d.textbbox((0, 0), "wastedmap.com", font=pill)
pw, ph = bx[2] - bx[0] + 44, 54
pill_bg = gradient((pw, ph), [(0, PINK), (.55, CORAL), (1, ORANGE)]).convert("RGBA")
pm = Image.new("L", (pw * 4, ph * 4), 0)
ImageDraw.Draw(pm).rounded_rectangle([0, 0, pw * 4 - 1, ph * 4 - 1], radius=ph * 2, fill=255)
pill_bg.putalpha(pm.resize((pw, ph), Image.LANCZOS))
og.alpha_composite(pill_bg, (66, 470))
d.text((88, 470 + (ph - (bx[3] - bx[1])) / 2 - bx[1]), "wastedmap.com", font=pill, fill=(26, 7, 18))
og.convert("RGB").save(DOCS / "og.png", optimize=True)
print("listo")
