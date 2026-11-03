"""Pest Vacuum sprite (32x32, drawn on the pixel grid): an aqua handheld bug vacuum, grip at the
bottom left, a glass canister with caught bugs in the middle, the nozzle reaching to the top
right. Also writes the brewing_stand item definition that shows it for items with
custom_model_data string "elytro:pest_vacuum"; without the pack the vacuum is a brewing stand.
Usage: python vac_build.py <out_dir>   (writes <out_dir>/assets/...; vac_preview.png next to this file)"""
import json, math, os, sys
from PIL import Image

T = 32
OUT = sys.argv[1] if len(sys.argv) > 1 else os.path.join(os.path.dirname(os.path.abspath(__file__)), 'netout')

BODY = [(120, 230, 230), (52, 186, 196), (28, 128, 140), (16, 84, 96)]     # hi, light, mid, dark
METAL = [(196, 202, 212), (140, 146, 158), (92, 98, 110), (58, 62, 72)]
BRASS = [(255, 220, 120), (214, 164, 54), (150, 104, 26)]
GLASS = [(226, 248, 252), (176, 226, 236), (128, 190, 206)]
GRIP = [(84, 70, 64), (54, 44, 40), (36, 28, 26)]
BUG = [(120, 210, 70), (58, 140, 40)]
OUTL = (26, 30, 38)


def draw():
    img = Image.new('RGBA', (T, T), (0, 0, 0, 0))
    px = img.load()
    solid = set()

    def put(x, y, c):
        if 0 <= x < T and 0 <= y < T:
            px[x, y] = c + (255,)
            solid.add((x, y))

    # nozzle: a 3-wide metal tube up to the top right, lit along its upper edge
    for i in range(0, 12):
        x, y = 17 + i, 13 - i
        put(x, y, METAL[1]); put(x - 1, y, METAL[0]); put(x, y + 1, METAL[2]); put(x + 1, y + 1, METAL[3])
    # brass nozzle tip
    for (x, y, c) in ((28, 1, 0), (29, 1, 1), (27, 2, 0), (28, 2, 1), (29, 2, 1), (30, 2, 2),
                      (28, 3, 1), (29, 3, 2), (30, 3, 2), (29, 4, 2)):
        put(x, y, BRASS[c])
    # brass collar where the nozzle meets the canister
    for (x, y, c) in ((16, 13, 0), (17, 14, 1), (16, 14, 1), (17, 15, 2), (18, 14, 2)):
        put(x, y, BRASS[c])
    # glass canister, a circle round (12.5, 17.5)
    cx, cy, r = 12.0, 17.0, 5.6
    for x in range(T):
        for y in range(T):
            d = math.hypot(x + 0.5 - cx, y + 0.5 - cy)
            if d < r:
                lit = (x + 0.5 - cx) + (y + 0.5 - cy) < -2
                c = GLASS[0] if lit else GLASS[1] if d < r - 1.4 else GLASS[2]
                put(x, y, c)
    # caught bugs inside
    for (bx, by) in ((10, 16), (13, 19), (14, 15)):
        put(bx, by, BUG[0]); put(bx + 1, by, BUG[1]); put(bx, by + 1, BUG[1])
    # a glint on the glass
    put(9, 14, (255, 255, 255)); put(10, 13, (255, 255, 255))
    # motor housing below the canister (aqua), with a dark band
    for x in range(3, 13):
        for y in range(21, 27):
            if (x - 3) + (26 - y) < 2 or (12 - x) + (26 - y) < 1:
                continue
            c = BODY[1] if y < 23 else BODY[2] if y < 25 else BODY[3]
            if x == 3 or y == 21:
                c = BODY[0]
            put(x, y, c)
    for x in range(4, 13):
        put(x, 23, BODY[3])
    for x in (6, 8, 10):   # vents
        put(x, 25, METAL[3])
    # grip, down to the bottom left
    for i in range(0, 5):
        x, y = 5 - i // 2, 27 + i // 1
        if y < T:
            put(x, y, GRIP[0]); put(x + 1, y, GRIP[1]); put(x + 2, y, GRIP[2])
    # trigger
    put(8, 27, METAL[2]); put(8, 28, METAL[3])
    # dark outline round everything
    for x in range(T):
        for y in range(T):
            if (x, y) not in solid and any((x + dx, y + dy) in solid for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1))):
                px[x, y] = OUTL + (255,)
    return img


def main():
    img = draw()
    tex = os.path.join(OUT, 'assets', 'elytro', 'textures', 'item')
    mod = os.path.join(OUT, 'assets', 'elytro', 'models', 'item')
    itm = os.path.join(OUT, 'assets', 'minecraft', 'items')
    for d in (tex, mod, itm):
        os.makedirs(d, exist_ok=True)
    img.save(os.path.join(tex, 'pest_vacuum.png'))
    json.dump({'parent': 'minecraft:item/handheld', 'textures': {'layer0': 'elytro:item/pest_vacuum'}},
              open(os.path.join(mod, 'pest_vacuum.json'), 'w'), indent=2)
    json.dump({'model': {'type': 'minecraft:select', 'property': 'minecraft:custom_model_data', 'index': 0,
                         'cases': [{'when': 'elytro:pest_vacuum',
                                    'model': {'type': 'minecraft:model', 'model': 'elytro:item/pest_vacuum'}}],
                         'fallback': {'type': 'minecraft:model', 'model': 'minecraft:item/brewing_stand'}}},
              open(os.path.join(itm, 'brewing_stand.json'), 'w'), indent=2)
    big = Image.new('RGBA', (T * 12 + 120, T * 12), (139, 139, 139, 255))
    big.alpha_composite(img.resize((T * 12, T * 12), Image.NEAREST))
    slot = Image.new('RGBA', (32, 32), (198, 198, 198, 255)); slot.alpha_composite(img)
    big.alpha_composite(slot, (T * 12 + 40, 40))
    big.save(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'vac_preview.png'))


if __name__ == '__main__':
    main()
