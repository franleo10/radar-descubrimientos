"""Genera los íconos PNG y la imagen para compartir de WastedMap (diseño propio)."""
import random
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageFont

DOCS = Path(sys.argv[1])
PINK, ORANGE, BG = (255, 61, 139), (255, 181, 71), (13, 11, 20)
FONT_B = "C:/Windows/Fonts/segoeuib.ttf"
FONT_R = "C:/Windows/Fonts/segoeui.ttf"


def gradient(size, c1, c2):
    w, h = size
    g = Image.new("RGB", size)
    px = g.load()
    for y in range(h):
        for x in range(w):
            t = (x / max(w - 1, 1) + y / max(h - 1, 1)) / 2
            px[x, y] = tuple(int(c1[i] + (c2[i] - c1[i]) * t) for i in range(3))
    return g


def pin_mask(size, s=4):
    """Silueta del pin (gota invertida) dibujada a escala s y reducida para suavizar."""
    w, h = size
    m = Image.new("L", (w * s, h * s), 0)
    d = ImageDraw.Draw(m)
    cx, r = w * s / 2, w * s * 0.42
    cy = r + h * s * 0.04
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=255)
    d.polygon([(cx - r * 0.86, cy + r * 0.5), (cx + r * 0.86, cy + r * 0.5), (cx, h * s * 0.98)], fill=255)
    hole = r * 0.4
    d.ellipse([cx - hole, cy - hole, cx + hole, cy + hole], fill=0)
    return m.resize(size, Image.LANCZOS)


def pin(size):
    img = gradient(size, PINK, ORANGE).convert("RGBA")
    img.putalpha(pin_mask(size))
    return img


def icon(px):
    s = 4
    base = Image.new("RGBA", (px * s, px * s), (0, 0, 0, 0))
    ImageDraw.Draw(base).rounded_rectangle([0, 0, px * s - 1, px * s - 1], radius=int(px * s * 0.22), fill=BG)
    base = base.resize((px, px), Image.LANCZOS)
    p = pin((int(px * 0.6), int(px * 0.78)))
    base.alpha_composite(p, ((px - p.width) // 2, int(px * 0.11)))
    return base


icon(180).save(DOCS / "apple-touch-icon.png")
icon(32).save(DOCS / "favicon-32.png")
icon(512).save(DOCS / "icon-512.png")

# --- Imagen para compartir (1200x630) ---
W, H = 1200, 630
og = Image.new("RGBA", (W, H), BG + (255,))
glow = gradient((W, H), (42, 15, 46), BG).convert("RGBA")
og.alpha_composite(glow)
grid = Image.new("RGBA", (W, H), (0, 0, 0, 0))
gd = ImageDraw.Draw(grid)
for x in range(0, W, 60):  # grilla tipo mapa, muy sutil
    gd.line([(x, 0), (x, H)], fill=(255, 255, 255, 12))
for y in range(0, H, 60):
    gd.line([(0, y), (W, y)], fill=(255, 255, 255, 12))
og.alpha_composite(grid)
d = ImageDraw.Draw(og)
# ruta punteada entre pines chicos
random.seed(7)
spots = [(80, 540), (190, 470), (290, 575), (390, 500)]
for (x1, y1), (x2, y2) in zip(spots, spots[1:]):
    for t in range(0, 20):
        if t % 2 == 0:
            a, b = t / 20, (t + 1) / 20
            d.line([(x1 + (x2 - x1) * a, y1 + (y2 - y1) * a), (x1 + (x2 - x1) * b, y1 + (y2 - y1) * b)],
                   fill=(46, 230, 214, 120), width=3)
for (x, y) in spots:
    p = pin((34, 44))
    og.alpha_composite(p, (x - 17, y - 44))

# pin grande con resplandor
big = pin((230, 300))
halo = Image.new("RGBA", (W, H), (0, 0, 0, 0))
halo.alpha_composite(Image.new("RGBA", big.size, PINK + (150,)), (150, 60))
halo.putalpha(Image.new("L", (W, H), 0))
shadow = Image.new("L", (W, H), 0)
shadow.paste(big.split()[3], (150, 60))
shadow = shadow.filter(ImageFilter.GaussianBlur(40))
og.alpha_composite(Image.merge("RGBA", (*Image.new("RGB", (W, H), PINK).split(), shadow.point(lambda v: v * 0.5))))
og.alpha_composite(big, (150, 60))

# texto
title_font = ImageFont.truetype(FONT_B, 112)
text = "WastedMap"
bbox = d.textbbox((0, 0), text, font=title_font)
tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
mask = Image.new("L", (W, H), 0)
ImageDraw.Draw(mask).text((450, 170), text, font=title_font, fill=255)
tg = Image.new("RGB", (W, H), ORANGE)
tg.paste(gradient((tw + 20, 140), PINK, ORANGE), (450, 170))
og.alpha_composite(Image.merge("RGBA", (*tg.split(), mask)))
d = ImageDraw.Draw(og)
sub = ImageFont.truetype(FONT_R, 40)
d.text((456, 330), "Todos los secretos que descubre", font=sub, fill=(236, 232, 245))
d.text((456, 380), "la comunidad de GTA 6", font=sub, fill=(236, 232, 245))
small = ImageFont.truetype(FONT_B, 30)
d.text((456, 470), "wastedmap.com", font=small, fill=(46, 230, 214))
d.text((456, 520), "Easter eggs · Lugares secretos · Autos · Guías", font=ImageFont.truetype(FONT_R, 26),
       fill=(154, 145, 173))
og.convert("RGB").save(DOCS / "og.png", optimize=True)
print("listo")
