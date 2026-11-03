"""Pest Net sprite (32x32, drawn on the pixel grid): a fishing net hanging from a head rope with
cork floats, diamond mesh, gathered at the bottom with a lead sinker. Also writes the cobweb item
definition that shows it for items with custom_model_data string "elytro:pest_net"; without the
pack the net is a cobweb.
Usage: python net_build.py <out_dir>   (writes <out_dir>/assets/...; net_preview.png next to this file)"""
import json, math, os, sys
from PIL import Image

T = 32
OUT = sys.argv[1] if len(sys.argv) > 1 else os.path.join(os.path.dirname(os.path.abspath(__file__)), 'netout')

ROPE = [(204, 160, 100), (164, 116, 64), (118, 80, 42)]      # light, mid, dark
TWINE = [(240, 234, 214), (196, 186, 156), (150, 138, 108)]
CORK = [(255, 196, 120), (232, 120, 60), (170, 70, 36)]
LEAD = [(206, 212, 220), (140, 148, 160), (88, 94, 106)]
OUTL = (52, 34, 18)


def half_width(y):
    """Half width of the net bag at row y: wide under the head rope, narrowing to the bottom knot."""
    t = (y - 6) / (27 - 6)
    return 12.5 * (1 - t ** 1.6) + 1.0


def draw():
    img = Image.new('RGBA', (T, T), (0, 0, 0, 0))
    px = img.load()
    solid = set()
    cx = 15.5

    def put(x, y, c):
        if 0 <= x < T and 0 <= y < T:
            px[x, y] = c + (255,)
            solid.add((x, y))

    inside = set()
    for y in range(7, 28):
        hw = half_width(y)
        for x in range(T):
            if abs(x + 0.5 - cx) <= hw:
                inside.add((x, y))
    # diamond mesh: diagonal twine both ways, lit on the upper left
    for (x, y) in inside:
        if (x + y) % 6 == 1 or (x - y) % 6 == 1:
            knot = (x + y) % 6 == 1 and (x - y) % 6 == 1
            shade = (x - cx) * 0.6 + (y - 16)
            c = TWINE[0] if shade < -3 else TWINE[1] if shade < 6 else TWINE[2]
            if knot:
                c = TWINE[1] if c == TWINE[0] else TWINE[2]
            put(x, y, c)
    # side lines of the bag
    for y in range(7, 28):
        hw = half_width(y)
        put(int(math.floor(cx - hw)), y, ROPE[1])
        put(int(math.ceil(cx + hw)) - 1, y, ROPE[2])
    # head rope across the top, twisted
    for x in range(1, 31):
        put(x, 5, ROPE[0] if x % 3 else ROPE[1])
        put(x, 6, ROPE[1] if x % 3 else ROPE[2])
    # cork floats on the head rope
    for fx in (3, 10, 18, 25):
        for (dx, dy, c) in ((1, 3, 0), (2, 3, 1), (0, 4, 0), (1, 4, 1), (2, 4, 1), (3, 4, 2),
                            (0, 5, 1), (1, 5, 1), (2, 5, 2), (3, 5, 2), (1, 6, 2), (2, 6, 2)):
            put(fx + dx, dy, CORK[c])
    # gathered bottom: a knot and a lead sinker
    for (x, y, c) in ((15, 27, ROPE[1]), (16, 27, ROPE[2]), (15, 28, ROPE[1]), (16, 28, ROPE[2]),
                      (14, 29, LEAD[0]), (15, 29, LEAD[0]), (16, 29, LEAD[1]), (17, 29, LEAD[2]),
                      (14, 30, LEAD[1]), (15, 30, LEAD[1]), (16, 30, LEAD[2]), (17, 30, LEAD[2])):
        put(x, y, c)
    # dark outline round the outside only (mesh holes stay see-through)
    for x in range(T):
        for y in range(T):
            if (x, y) in inside:
                continue
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
    img.save(os.path.join(tex, 'pest_net.png'))
    json.dump({'parent': 'minecraft:item/generated', 'textures': {'layer0': 'elytro:item/pest_net'}},
              open(os.path.join(mod, 'pest_net.json'), 'w'), indent=2)
    json.dump({'model': {'type': 'minecraft:select', 'property': 'minecraft:custom_model_data', 'index': 0,
                         'cases': [{'when': 'elytro:pest_net',
                                    'model': {'type': 'minecraft:model', 'model': 'elytro:item/pest_net'}}],
                         'fallback': {'type': 'minecraft:model', 'model': 'minecraft:item/cobweb'}}},
              open(os.path.join(itm, 'cobweb.json'), 'w'), indent=2)
    bg = Image.new('RGBA', (T * 12, T * 12), (139, 139, 139, 255))
    bg.alpha_composite(img.resize((T * 12, T * 12), Image.NEAREST))
    bg.save(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'net_preview.png'))


if __name__ == '__main__':
    main()
