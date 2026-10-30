"""Geass - a helmet skin (Lelouch's Geass from Code Geass): any helmet becomes invisible except for
a glowing red Geass sigil over the wearer's left eye. Activated (sneak + swap hands, or /geass),
the sigil flares into its full winged form and the wearer's screen takes on a red vignette.

Worn looks are equipment textures (the humanoid layer, 8x resolution so the sigil keeps its
shape inside a two-pixel eye). The armour layer is drawn 1.25x the size of the head, so the eye
is placed scaled back toward the face's centre to land on the skin's own eye.

Writes into ./assets/elytro (this folder):
  equipment/geass.json, equipment/geass_active.json
  textures/entity/equipment/humanoid/geass.png, geass_active.png
  textures/misc/geass_overlay.png      (camera overlay while active)
  items/geass.json, models/item/geass.json, textures/item/geass.png (inventory/hand icon)
Usage (needs Pillow): python geass_build.py
"""
import json
import math
import os

from PIL import Image, ImageDraw, ImageFilter

HERE = os.path.dirname(os.path.abspath(__file__))
A = os.path.join(HERE, 'assets', 'elytro')
X = 8                                   # texture scale: 512x256 humanoid layer

RED = (255, 30, 64)
CORE = (255, 132, 156)
DEEP = (150, 0, 26)


def sigil(size, wings=1.0, stroke=1.0, iris=False):
    """The Geass bird at `size` px (RGBA, hard edges): a head, a long diamond body ending in a
    pointed tail, and two blade-like wings sweeping up and out to sharp tips, each cut by two
    feather notches. `wings` scales the span; `iris` puts it on a red iris, as in the eye."""
    S = 8
    W = size * S
    im = Image.new('L', (W, W), 0)
    d = ImageDraw.Draw(im)
    c = W / 2

    def p(x, y):                         # x, y in -1..1
        return (c + x * W * 0.47, c + y * W * 0.47)

    # body and tail: one long diamond, widest at the shoulders
    d.polygon([p(0, -0.5), p(0.15, -0.08), p(0.05, 0.45), p(0, 0.9), p(-0.05, 0.45), p(-0.15, -0.08)], fill=255)
    # head
    d.polygon([p(0, -0.8), p(0.1, -0.64), p(0, -0.52), p(-0.1, -0.64)], fill=255)
    for side in (-1, 1):
        # upper edge: shoulder up and out to the tip; lower edge: back in, curving under
        top = [(side * (0.12 + 0.86 * wings * t), -0.12 - 0.62 * wings * math.sin(t * math.pi * 0.5) ** 0.8) for t in (i / 24 for i in range(25))]
        tip = top[-1]
        low = [(side * (0.12 + (abs(tip[0]) - 0.12) * (1 - t)), tip[1] + (0.22 - tip[1]) * t ** 0.7 + 0.18 * math.sin(t * math.pi)) for t in (i / 24 for i in range(1, 25))]
        d.polygon([p(x, y) for x, y in top + low], fill=255)
        # feather notches cut into the wing's trailing edge
        for k in (0.42, 0.66):
            x0 = side * (0.12 + (abs(tip[0]) - 0.12) * k)
            d.line([p(x0, 0.2), p(x0 + side * 0.08, -0.12 - 0.3 * wings * k)], fill=0, width=max(2, int(W * 0.035 * stroke)))
    mask = im.resize((size, size), Image.LANCZOS)
    core = im.filter(ImageFilter.MinFilter(max(3, int(W * 0.06) | 1))).resize((size, size), Image.LANCZOS)
    out = Image.new('RGBA', (size, size), (0, 0, 0, 0))
    if iris:
        ImageDraw.Draw(out).ellipse([0, 0, size - 1, size - 1], fill=(110, 0, 20, 255), outline=DEEP + (255,))
    px = out.load()
    for y in range(size):
        for x in range(size):
            a = mask.getpixel((x, y))
            if a < 100:
                continue
            col = CORE if core.getpixel((x, y)) > 150 else RED
            px[x, y] = col + (255,)
    if iris:
        return out
    # a deep red rim round the glyph so it reads on any skin
    rim = Image.new('RGBA', (size, size), (0, 0, 0, 0))
    rp = rim.load()
    for y in range(size):
        for x in range(size):
            if px[x, y][3]:
                continue
            if any(0 <= x + dx < size and 0 <= y + dy < size and px[x + dx, y + dy][3] for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1))):
                rp[x, y] = DEEP + (255,)
    rim.alpha_composite(out)
    return rim


# where the eye goes, in helmet-face pixels (0..8 across the face): the skin's left eye (the
# viewer's right) sits at about x 6.0, y 4.25; the helmet face is 1.25x the head, so scale back
EYE_X = 4 + (6.0 - 4) / 1.25
EYE_Y = 4 + (4.25 - 4) / 1.25


def layer(active):
    tex = Image.new('RGBA', (64 * X, 32 * X), (0, 0, 0, 0))
    cx, cy = (8 + EYE_X) * X, (8 + EYE_Y) * X
    if active:
        # the full sigil, wings spread wide across the face, and a ring round the eye
        g = sigil(36, wings=1.0, stroke=0.9)
        ring = Image.new('RGBA', (20, 20), (0, 0, 0, 0))
        ImageDraw.Draw(ring).ellipse([1, 1, 18, 18], outline=DEEP + (255,), width=2)
        tex.alpha_composite(ring, (int(cx - 10), int(cy - 10)))
    else:
        g = sigil(16, wings=0.85, iris=True)
    tex.alpha_composite(g, (int(cx - g.width / 2), int(cy - g.height / 2)))
    return tex


def overlay():
    """A red vignette for the wearer's screen while the Geass is active, with the sigil's wings
    faintly at the edges. Camera overlays are stretched over the screen and keep their alpha."""
    W, H = 512, 256
    im = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    px = im.load()
    for y in range(H):
        for x in range(W):
            dx, dy = (x - W / 2) / (W / 2), (y - H / 2) / (H / 2)
            r = math.hypot(dx * 0.95, dy)
            a = max(0.0, min(1.0, (r - 0.55) / 0.6)) ** 1.6
            px[x, y] = (150, 0, 30, int(150 * a))
    wing = sigil(200, wings=1.0, stroke=0.6)
    wing = wing.resize((380, 380), Image.LANCZOS)
    faint = Image.new('RGBA', wing.size, (0, 0, 0, 0))
    fp, wp = faint.load(), wing.load()
    for y in range(wing.height):
        for x in range(wing.width):
            r, g, b, a = wp[x, y]
            if a:
                fp[x, y] = (255, 40, 70, 34)
    im.alpha_composite(faint, ((W - 380) // 2, (H - 380) // 2 + 20))
    return im


def icon():
    """The inventory/hand icon: the sigil itself, on a dark disc."""
    S = 8
    big = Image.new('RGBA', (32 * S, 32 * S), (0, 0, 0, 0))
    d = ImageDraw.Draw(big)
    d.ellipse([2 * S, 2 * S, 30 * S, 30 * S], fill=(20, 4, 10, 255), outline=(120, 0, 24, 255), width=S)
    small = big.resize((32, 32), Image.LANCZOS)
    px = small.load()
    for y in range(32):
        for x in range(32):
            r, g, b, a = px[x, y]
            px[x, y] = (r, g, b, 255 if a > 110 else 0)
    g = sigil(26, wings=1.0, stroke=1.1)
    small.alpha_composite(g, (3, 4))
    return small


def write(rel, data):
    path = os.path.join(A, rel)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    if isinstance(data, Image.Image):
        data.save(path)
    else:
        with open(path, 'w', encoding='utf-8', newline='\n') as f:
            json.dump(data, f, indent=1)


def build():
    write('textures/entity/equipment/humanoid/geass.png', layer(False))
    write('textures/entity/equipment/humanoid/geass_active.png', layer(True))
    write('equipment/geass.json', {'layers': {'humanoid': [{'texture': 'elytro:geass'}]}})
    write('equipment/geass_active.json', {'layers': {'humanoid': [{'texture': 'elytro:geass_active'}]}})
    write('textures/misc/geass_overlay.png', overlay())
    write('textures/item/geass.png', icon())
    write('models/item/geass.json', {'parent': 'minecraft:item/generated', 'textures': {'layer0': 'elytro:item/geass'}})
    write('items/geass.json', {'model': {'type': 'minecraft:model', 'model': 'elytro:item/geass'}})
    print('Geass: eye at helmet face (%.2f, %.2f)' % (EYE_X, EYE_Y))


if __name__ == '__main__':
    build()
