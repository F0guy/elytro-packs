"""Takuni Transplant Chip sprite (32x32, drawn on the pixel grid), 2026-11-07.
A grafted nerve chip for the Harvest Strider recipe: a dark circuit-board chip with brass pins and
teal (#5FD3C6) traces, a raw red nerve bulb (with a pupil, a nod to the spider eye) grafted into
the middle, and pink nerve strands trailing out of the bottom, clamped with brass.
Also writes the spider_eye item definition: items with custom_model_data string
"elytro:takuni_chip" show the chip; everything else stays a spider eye.
Usage: python -I takuni_chip_build.py <assets out dir> <preview.png>
"""
import json, os, sys
from PIL import Image

OUT, PREVIEW = sys.argv[1], sys.argv[2]
T = 32

BOARD = [(58, 84, 82), (38, 58, 58), (24, 38, 40)]        # light, mid, dark
TEAL = [(176, 246, 236), (95, 211, 198), (44, 130, 124)]  # #5FD3C6 in the middle
BRASS = [(240, 204, 120), (196, 150, 70), (122, 86, 38)]
FLESH = [(255, 150, 150), (206, 64, 70), (122, 26, 38)]
NERVE = [(255, 196, 196), (226, 128, 140), (150, 64, 84)]
PUPIL = (30, 8, 14)
OUTL = (14, 20, 22)

img = Image.new('RGBA', (T, T), (0, 0, 0, 0))
px = img.load()


def put(x, y, c):
    if 0 <= x < T and 0 <= y < T:
        px[x, y] = c + (255,)


# ---- chip body: rows 5..22, cols 7..24, bevelled corners, lit from the upper left
X0, X1, Y0, Y1 = 7, 24, 5, 22
for y in range(Y0, Y1 + 1):
    for x in range(X0, X1 + 1):
        if (x, y) in ((X0, Y0), (X1, Y0), (X0, Y1), (X1, Y1)):
            continue
        c = BOARD[1]
        if x == X0 or y == Y0:
            c = BOARD[0]
        elif x == X1 or y == Y1:
            c = BOARD[2]
        put(x, y, c)

# brass pins, left and right edges, every other row
for y in range(Y0 + 2, Y1 - 1, 2):
    put(X0 - 1, y, BRASS[1]); put(X0 - 2, y, BRASS[0])
    put(X1 + 1, y, BRASS[1]); put(X1 + 2, y, BRASS[2])
# top pins
for x in range(X0 + 3, X1 - 2, 3):
    put(x, Y0 - 1, BRASS[0]); put(x, Y0 - 2, BRASS[1])

# teal traces running from the pins toward the core
traces = [
    [(9, 7), (10, 7), (11, 7), (12, 7), (12, 8), (12, 9)],
    [(22, 7), (21, 7), (20, 7), (19, 7), (19, 8), (19, 9)],
    [(9, 11), (10, 11), (11, 11)],
    [(22, 11), (21, 11), (20, 11)],
    [(9, 15), (10, 15), (11, 15), (11, 16), (11, 17), (12, 18)],
    [(22, 15), (21, 15), (20, 15), (20, 16), (20, 17), (19, 18)],
    [(14, 7), (14, 8)], [(17, 7), (17, 8)],
]
for tr in traces:
    for i, (x, y) in enumerate(tr):
        put(x, y, TEAL[1] if i else TEAL[0])
# trace pads (lit dots)
for (x, y) in ((9, 7), (22, 7), (9, 11), (22, 11), (9, 15), (22, 15), (14, 7), (17, 7)):
    put(x, y, TEAL[0])
# a few dim etched lines for texture
for (x, y) in ((9, 19), (10, 20), (21, 19), (22, 20), (9, 9), (22, 9)):
    put(x, y, BOARD[2])

# ---- grafted nerve bulb in the middle (rows 9..17, cols 12..19) with a teal socket ring
ring = [(13, 9), (14, 9), (15, 9), (16, 9), (17, 9), (18, 9),
        (12, 10), (19, 10), (12, 11), (19, 11), (12, 12), (19, 12), (12, 13), (19, 13),
        (12, 14), (19, 14), (12, 15), (19, 15), (12, 16), (19, 16),
        (13, 17), (14, 17), (15, 17), (16, 17), (17, 17), (18, 17)]
for (x, y) in ring:
    put(x, y, TEAL[2] if x >= 18 or y >= 16 else TEAL[1])
for y in range(10, 17):
    for x in range(13, 19):
        d = (x - 15.5) ** 2 / 9 + (y - 13.2) ** 2 / 12
        c = FLESH[0] if (x <= 14 and y <= 12) else FLESH[2] if (x >= 18 or y >= 16) else FLESH[1]
        if d > 1.05:
            c = FLESH[2]
        put(x, y, c)
# round the bulb's corners into the socket ring
for (x, y) in ((13, 10), (18, 10), (13, 16), (18, 16)):
    put(x, y, TEAL[2] if x == 18 or y == 16 else TEAL[1])
# pupil and a wet highlight
for (x, y) in ((15, 13), (16, 13), (15, 14), (16, 14)):
    put(x, y, PUPIL)
put(16, 12, FLESH[2])
put(14, 11, (255, 236, 236))
put(13, 11, FLESH[0])

# ---- nerve strands out of the bottom edge, each with a brass clamp
strands = [
    [(13, 23), (13, 24), (12, 25), (11, 26), (11, 27), (10, 28), (9, 29)],
    [(16, 23), (16, 24), (16, 25), (17, 26), (17, 27), (16, 28), (16, 29), (17, 30)],
    [(19, 23), (19, 24), (20, 25), (21, 26), (22, 27), (22, 28), (23, 29)],
]
for st in strands:
    for i, (x, y) in enumerate(st):
        c = NERVE[0] if i % 3 == 0 else NERVE[1]
        if i == len(st) - 1:
            c = NERVE[2]
        put(x, y, c)
    cx, cy = st[1]
    put(cx - 1, cy, BRASS[1]); put(cx + 1, cy, BRASS[2]); put(cx, cy, BRASS[0])

# ---- outline: dark pixel around every solid pixel
solid = {(x, y) for y in range(T) for x in range(T) if px[x, y][3]}
for y in range(T):
    for x in range(T):
        if (x, y) in solid:
            continue
        if any((x + dx, y + dy) in solid for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1))):
            put(x, y, OUTL)

TEX = os.path.join(OUT, 'elytro', 'textures', 'item')
MOD = os.path.join(OUT, 'elytro', 'models', 'item')
ITM = os.path.join(OUT, 'minecraft', 'items')
for d in (TEX, MOD, ITM):
    os.makedirs(d, exist_ok=True)
img.save(os.path.join(TEX, 'takuni_chip.png'))
json.dump({'parent': 'minecraft:item/generated', 'textures': {'layer0': 'elytro:item/takuni_chip'}},
          open(os.path.join(MOD, 'takuni_chip.json'), 'w'), indent=2)
json.dump({'model': {
    'type': 'minecraft:select', 'property': 'minecraft:custom_model_data', 'index': 0,
    'cases': [{'when': 'elytro:takuni_chip',
               'model': {'type': 'minecraft:model', 'model': 'elytro:item/takuni_chip'}}],
    'fallback': {'type': 'minecraft:model', 'model': 'minecraft:item/spider_eye'}}},
    open(os.path.join(ITM, 'spider_eye.json'), 'w'), indent=2)

prev = Image.new('RGBA', (T * 10, T * 10), (40, 40, 46, 255))
big = img.resize((T * 10, T * 10), Image.NEAREST)
prev.paste(big, (0, 0), big)
prev.save(PREVIEW)
print('ok')
