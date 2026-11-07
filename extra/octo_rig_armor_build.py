"""Octo Rig chestplate: its own worn look and inventory icon (2026-11-07).
Usage: python -I octo_rig_armor_build.py <assets out dir> <preview.png>

Writes, under <out>/elytro/:
  equipment/octo_rig.json                          worn look (equippable asset_id elytro:octo_rig)
  textures/entity/equipment/humanoid/octo_rig.png  64x32 humanoid sheet: body + arms (head/legs empty)
  textures/item/octo_rig_chest.png                 16x16 inventory icon
  models/item/octo_rig_chest.json, items/octo_rig_chest.json   (item_model elytro:octo_rig_chest)

Look (farm restyle 2026-11-07): oiled leather harness, brass fittings and straps crossing the
chest, a glowing green core, a riveted back plate where the arm hub sits, segmented leather
pauldrons. Original pixel art; no vanilla textures.
"""
import json, os, random, sys
from PIL import Image

OUT, PREVIEW = sys.argv[1], sys.argv[2]
EQ = os.path.join(OUT, 'elytro', 'equipment')
HUM = os.path.join(OUT, 'elytro', 'textures', 'entity', 'equipment', 'humanoid')
TEX = os.path.join(OUT, 'elytro', 'textures', 'item')
MOD = os.path.join(OUT, 'elytro', 'models', 'item')
ITM = os.path.join(OUT, 'elytro', 'items')
for d in (EQ, HUM, TEX, MOD, ITM):
    os.makedirs(d, exist_ok=True)

# farm look (nikoc 2026-11-07: fit the farming theme): oiled leather harness, brass fittings,
# a green "chlorophyll" core. The names stay STEEL/DARK so the drawing code below is unchanged.
STEEL = (124, 82, 48)    # oiled saddle leather
DARK = (82, 54, 32)      # darker leather / shadow
EDGE = (44, 28, 16)
BRASS = (182, 136, 64)
BRASS_HI = (222, 178, 98)
BRASS_LO = (122, 88, 38)
CORE = (112, 214, 64)
CORE_HI = (206, 255, 160)
CORE_LO = (46, 124, 30)
rng = random.Random(7)


def sh(c, f):
    return tuple(max(0, min(255, int(v * f))) for v in c[:3]) + (255,)


def faces(u, v, w, h, d):
    return {
        'top': (u + d, v, w, d), 'bottom': (u + d + w, v, w, d),
        'right': (u, v + d, d, h), 'front': (u + d, v + d, w, h),
        'left': (u + d + w, v + d, d, h), 'back': (u + 2 * d + w, v + d, w, h),
    }


BODY = faces(16, 16, 8, 12, 4)
ARM = faces(40, 16, 4, 12, 4)

img = Image.new('RGBA', (64, 32), (0, 0, 0, 0))
px = img.load()


def put(x, y, c):
    if 0 <= x < 64 and 0 <= y < 32:
        px[x, y] = c if len(c) == 4 else c + (255,)


def face_fill(f, base, noise=0.05, vgrad=0.18):
    x0, y0, w, h = f
    for y in range(h):
        for x in range(w):
            g = 1.08 - vgrad * y / max(1, h - 1)
            put(x0 + x, y0 + y, sh(base, g * (1 + rng.uniform(-noise, noise))))


# ---- body: steel cuirass
for k in ('front', 'back', 'right', 'left', 'top', 'bottom'):
    face_fill(BODY[k], STEEL if k in ('front', 'back') else DARK)

fx, fy, fw, fh = BODY['front']
# collar and waist rims
for x in range(fw):
    put(fx + x, fy, BRASS_LO)
    put(fx + x, fy + fh - 1, BRASS_LO)
    put(fx + x, fy + fh - 2, sh(DARK, 1.0))
# darker side edges of the chest plate
for x in (0, 7):
    for y in range(1, fh - 2):
        put(fx + x, fy + y, sh(STEEL, 0.72))
# brass harness straps crossing (shoulder -> opposite hip)
for i in range(10):
    y = fy + 1 + i
    for x, c in ((fx + min(7, i * 7 // 9), BRASS), (fx + 7 - min(7, i * 7 // 9), BRASS)):
        put(x, y, c)
for i in range(10):  # lit edge under each strap
    y = fy + 2 + i
    if y < fy + fh - 2:
        put(fx + min(7, i * 7 // 9), y, sh(BRASS_LO, 1.0)) if i % 3 == 2 else None
# glowing core where the straps cross
cx, cy = fx + 3, fy + 5
for (dx, dy) in ((0, 0), (1, 0), (0, 1), (1, 1)):
    put(cx + dx, cy + dy, CORE)
put(cx, cy, CORE_HI)
for (dx, dy) in ((-1, 0), (2, 0), (-1, 1), (2, 1), (0, -1), (1, -1), (0, 2), (1, 2)):
    put(cx + dx, cy + dy, BRASS_HI)
# belly bands
for y in (fy + 8, fy + 9):
    for x in range(1, 7):
        if (x + y) % 3:
            put(fx + x, y, sh(STEEL, 0.85 if y == fy + 8 else 1.1))

bx, by, bw, bh = BODY['back']
# back plate (the arm hub sits on this): brass frame, rivets, dark vents
for x in range(1, bw - 1):
    put(bx + x, by + 2, BRASS)
    put(bx + x, by + 9, BRASS_LO)
for y in range(2, 10):
    put(bx + 1, by + y, BRASS)
    put(bx + bw - 2, by + y, BRASS_LO)
for (rx, ry) in ((2, 3), (5, 3), (2, 8), (5, 8)):
    put(bx + rx, by + ry, BRASS_HI)
for y in range(4, 8):
    for x in range(3, 5):
        put(bx + x, by + y, EDGE if y % 2 == 0 else sh(DARK, 1.2))
for x in range(bw):
    put(bx + x, by, BRASS_LO)
    put(bx + x, by + bh - 1, BRASS_LO)
# sides: strap ends
for k in ('right', 'left'):
    x0, y0, w, h = BODY[k]
    for y in range(h):
        put(x0 + 1, y0 + y, sh(DARK, 0.85))
    put(x0 + 1, y0 + 10, BRASS)
    put(x0 + 2, y0 + 10, BRASS)

# ---- arms: segmented steel pauldrons on the top third, the rest left empty (skin shows)
for k in ('front', 'back', 'right', 'left', 'top'):
    x0, y0, w, h = ARM[k]
    rows = h if k == 'top' else 5
    for y in range(rows):
        for x in range(w):
            base = STEEL if y in (0, 1, 3) else DARK
            if k != 'top' and y == 2:
                base = BRASS_LO
            if k != 'top' and y == 4:
                base = BRASS
            put(x0 + x, y0 + y, sh(base, 1.05 - 0.06 * y + rng.uniform(-0.04, 0.04)))
# a rivet on the outer side of each pauldron
x0, y0, w, h = ARM['right']
put(x0 + 1, y0 + 1, BRASS_HI)
put(x0 + 2, y0 + 1, BRASS_HI)

img.save(os.path.join(HUM, 'octo_rig.png'))
json.dump({'layers': {'humanoid': [{'texture': 'elytro:octo_rig'}]}},
          open(os.path.join(EQ, 'octo_rig.json'), 'w'), indent=2)

# ---- 16x16 inventory icon: front view of the cuirass with the core and two curling arms
icon = Image.new('RGBA', (16, 16), (0, 0, 0, 0))
ip = icon.load()


def ip_put(x, y, c):
    if 0 <= x < 16 and 0 <= y < 16:
        ip[x, y] = c if len(c) == 4 else c + (255,)


shape = [
    "................",
    "...BB......BB...",
    "..BSSB....BSSB..",
    ".BSSSSBBBBSSSSB.",
    ".BSSSSSSSSSSSSB.",
    "..BSSSSSSSSSSB..",
    "...SSSSSSSSSS...",
    "...SSSSSSSSSS...",
    "...SSSSSSSSSS...",
    "...SSSSSSSSSS...",
    "...SSSSSSSSSS...",
    "...BBBBBBBBBB...",
    "...DDDDDDDDDD...",
    "....DDDDDDDD....",
    "................",
    "................",
]
for y, row in enumerate(shape):
    for x, ch in enumerate(row):
        if ch == 'S':
            f = 1.15 - 0.45 * (y / 13) - (0.18 if x in (3, 12) else 0) + (0.12 if x in (5, 6) else 0)
            ip_put(x, y, sh(STEEL, f))
        elif ch == 'B':
            ip_put(x, y, sh(BRASS, 1.1 - 0.3 * (y / 13)))
        elif ch == 'D':
            ip_put(x, y, sh(DARK, 1.0))
# straps crossing
for i in range(7):
    ip_put(4 + i, 4 + i, BRASS)
    ip_put(11 - i, 4 + i, BRASS)
# core
for (x, y, c) in ((7, 7, CORE_HI), (8, 7, CORE), (7, 8, CORE), (8, 8, CORE_LO)):
    ip_put(x, y, c)
# outline
mask = [[ip[x, y][3] > 0 for x in range(16)] for y in range(16)]
for y in range(16):
    for x in range(16):
        if not mask[y][x] and any(0 <= x + dx < 16 and 0 <= y + dy < 16 and mask[y + dy][x + dx]
                                  for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1))):
            ip_put(x, y, EDGE)
# two arm curls hanging off the hips
for (x, y) in ((2, 11), (1, 12), (1, 13), (2, 14), (3, 14), (13, 11), (14, 12), (14, 13), (13, 14), (12, 14)):
    ip_put(x, y, sh(STEEL, 0.9))
for (x, y) in ((3, 14), (12, 14)):
    ip_put(x, y, BRASS)
icon.save(os.path.join(TEX, 'octo_rig_chest.png'))

json.dump({'parent': 'minecraft:item/generated', 'textures': {'layer0': 'elytro:item/octo_rig_chest'}},
          open(os.path.join(MOD, 'octo_rig_chest.json'), 'w'), indent=2)
json.dump({'model': {'type': 'minecraft:model', 'model': 'elytro:item/octo_rig_chest'}},
          open(os.path.join(ITM, 'octo_rig_chest.json'), 'w'), indent=2)

# ---- preview: sheet x8 and icon x16 side by side
prev = Image.new('RGBA', (64 * 8 + 16 * 16 + 24, 32 * 8 if 32 * 8 > 256 else 256), (40, 40, 46, 255))
prev.paste(img.resize((512, 256), Image.NEAREST), (0, 0), img.resize((512, 256), Image.NEAREST))
ic = icon.resize((256, 256), Image.NEAREST)
prev.paste(ic, (512 + 24, 0), ic)
prev.save(PREVIEW)
print('ok')
