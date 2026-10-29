"""Inventory icons (32x32, flat, bold, filling the slot) for the Key to the City and the Bug Net.
The items keep their held look; their item definitions show these icons only in GUIs (and
item frames). Shapes are drawn smooth at 128px, reduced to 32x32 masks, then shaded per
material like vanilla items (lit up-left, shaded down-right, outlined).
Writes into ./assets/elytro (this folder). Run after key_to_city_build.py."""
import json, math, os
from PIL import Image, ImageDraw

B, T = 128, 32
A = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'assets', 'elytro')


def canvas():
    im = Image.new('L', (B, B), 0)
    return im, ImageDraw.Draw(im)


def bez(p0, p1, p2, n=40):
    return [((1 - t) ** 2 * p0[0] + 2 * (1 - t) * t * p1[0] + t * t * p2[0],
             (1 - t) ** 2 * p0[1] + 2 * (1 - t) * t * p1[1] + t * t * p2[1]) for t in (k / n for k in range(n + 1))]


def reduce(im, threshold=100):
    small = im.resize((T, T), Image.BOX)
    return {(x, y) for x in range(T) for y in range(T) if small.getpixel((x, y)) >= threshold}


def shade(px, mask, pal, solid=None):
    """pal = (highlight, light, mid, dark, deep). Pixels open to the up-left are lit, those
    open to the down-right are shaded; `solid` is everything that counts as filled."""
    solid = solid or mask
    hi, l, m, d, lo = pal
    for (x, y) in mask:
        c = m
        if (x - 1, y) not in solid or (x, y - 1) not in solid:
            c = hi if (x - 1, y) not in solid and (x, y - 1) not in solid else l
        elif (x + 1, y) not in solid or (x, y + 1) not in solid:
            c = lo if (x + 1, y) not in solid and (x, y + 1) not in solid else d
        px[x, y] = c + (255,)


def outline(px, solid, colour):
    for x in range(T):
        for y in range(T):
            if (x, y) not in solid and any((x + dx, y + dy) in solid for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1))):
                px[x, y] = colour + (255,)


# ---------------------------------------------------------------- Key to the City icon
def key_icon():
    """Drawn straight onto the 32x32 grid (no shrinking), so every stroke is whole pixels:
    a 2px shaft with two collar ticks, a toothed bar at the grip end, a figure-eight bow of two
    small rings, and a slim crescent blade."""
    im = Image.new('L', (T, T), 0)
    d = ImageDraw.Draw(im)
    d.line([(4, 28), (17, 15)], fill=255, width=2)                  # shaft
    for (x, y) in ((9, 23), (13, 19)):                               # collar ticks
        d.line([(x - 1, y - 1), (x + 1, y + 1)], fill=255, width=1)
        d.line([(x - 2, y - 1), (x + 1, y + 2)], fill=255, width=1)
    d.line([(3, 26), (8, 26)], fill=255, width=2)                    # the bit: a bar at the grip end
    for x in (3, 6, 8):                                              # with three teeth hanging off it
        d.line([(x, 27), (x, 29)], fill=255, width=1)
    d.ellipse([14, 8, 21, 15], outline=255, width=2)                 # lower ring
    d.ellipse([19, 2, 26, 9], outline=255, width=2)                  # upper ring
    d.polygon([(24, 2), (27, 3), (30, 8), (31, 15), (29, 23), (26, 29), (25, 29),
               (27, 22), (28, 15), (27, 9), (25, 7)], fill=255)      # blade
    im = im.transpose(Image.TRANSVERSE)                              # turned around, like the held sprite
    mask = {(x, y) for x in range(T) for y in range(T) if im.getpixel((x, y)) > 0}
    img = Image.new('RGBA', (T, T), (0, 0, 0, 0))
    px = img.load()
    shade(px, mask, ((255, 246, 176), (255, 224, 90), (246, 190, 38), (206, 140, 16), (176, 112, 10)))
    outline(px, mask, (110, 64, 4))
    return img


# ---------------------------------------------------------------- Bug Net icon
def bug_net_icon():
    # seen at an angle: the hoop as a tilted oval at the top right, the net bag drooping out
    # of it down to the right, the bamboo handle running in from the bottom left with a cord
    # collar where it meets the hoop
    hoop, dr = canvas()
    ring = Image.new('L', (B, B), 0)
    rd = ImageDraw.Draw(ring)
    rd.ellipse([24, 34, 104, 94], outline=255, width=8)          # an oval, then turned 45
    ring = ring.rotate(45, resample=Image.BICUBIC, center=(64, 64))
    hoop.paste(ring.transform((B, B), Image.AFFINE, (1, 0, -14, 0, 1, 14)), (0, 0))   # up and right
    inside = Image.new('L', (B, B), 0)
    idr = ImageDraw.Draw(inside)
    idr.ellipse([30, 40, 98, 88], fill=255)
    inside = inside.rotate(45, resample=Image.BICUBIC, center=(64, 64)).transform((B, B), Image.AFFINE, (1, 0, -14, 0, 1, 14))
    bag = Image.new('L', (B, B), 0)
    bd = ImageDraw.Draw(bag)
    bd.polygon([(70, 40), (106, 54), (118, 96), (110, 120), (92, 112), (66, 70)], fill=255)
    bd.ellipse([94, 100, 120, 124], fill=255)
    handle, dh = canvas()
    dh.line([(10, 120), (52, 78)], fill=255, width=11)
    collar, dc = canvas()
    dc.line([(44, 86), (56, 74)], fill=255, width=15)
    m_handle, m_hoop, m_collar = reduce(handle), reduce(hoop, 90), reduce(collar)
    m_net = (reduce(inside, 120) | reduce(bag, 120))
    solid = m_handle | m_hoop | m_collar
    img = Image.new('RGBA', (T, T), (0, 0, 0, 0))
    px = img.load()
    # mesh: a loose diamond lattice of white threads, see-through between them, a bit greyer
    # in the bag (the back of the net)
    in_hoop = reduce(inside, 120)
    mesh = {(x, y) for (x, y) in m_net - solid if (x + y) % 5 == 0 or (x - y) % 5 == 0}
    for (x, y) in mesh:
        px[x, y] = ((246, 249, 253) if (x, y) in in_hoop else (206, 214, 226)) + (255,)
    shade(px, m_handle, ((246, 222, 156), (232, 196, 120), (214, 170, 92), (182, 138, 66), (150, 108, 48)))
    for (x, y) in m_handle:                       # bamboo node bands
        if (x - y) % 7 == 0:
            px[x, y] = (150, 108, 52, 255)
    shade(px, m_hoop, ((255, 244, 206), (250, 232, 182), (240, 214, 150), (214, 186, 120), (186, 156, 96)))
    shade(px, m_collar, ((206, 152, 84), (190, 140, 72), (160, 112, 56), (132, 88, 44), (108, 70, 34)))
    for (x, y) in m_collar:                       # the wrapped cord
        if (x + y) % 2 == 0:
            px[x, y] = (120, 80, 40, 255)
    # the net's outline, light, so it stays airy; the solid parts get the dark one
    for x in range(T):
        for y in range(T):
            if (x, y) in m_net and (x, y) not in mesh and (x, y) not in solid:
                edge = any((x + dx, y + dy) not in m_net and (x + dx, y + dy) not in solid
                           for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)))
                if edge:
                    px[x, y] = (196, 204, 216, 255)
    outline(px, solid, (52, 36, 20))
    return img


def write(rel, obj):
    p = os.path.join(A, rel)
    os.makedirs(os.path.dirname(p), exist_ok=True)
    with open(p, 'w', newline='\n') as f:
        json.dump(obj, f, indent=1)
        f.write('\n')


icons = {'key_to_city_icon': key_icon(), 'bug_net_icon': bug_net_icon()}
os.makedirs(os.path.join(A, 'textures', 'item'), exist_ok=True)
for name, img in icons.items():
    img.save(os.path.join(A, 'textures', 'item', name + '.png'))
    write('models/item/%s.json' % name, {'parent': 'minecraft:item/generated', 'textures': {'layer0': 'elytro:item/' + name}})


def by_context(held):
    """The held model everywhere, the flat icon in inventories and item frames."""
    return {'model': {'type': 'minecraft:select', 'property': 'minecraft:display_context',
                      'cases': [{'when': ['gui', 'fixed'], 'model': {'type': 'minecraft:model', 'model': held + '_icon'}}],
                      'fallback': {'type': 'minecraft:model', 'model': held}}}


write('items/key_to_city.json', by_context('elytro:item/key_to_city'))
write('items/bug_net.json', by_context('elytro:item/bug_net'))

# the key in hand: a normal (extruded, 3D) item sprite, held about 30% bigger than a vanilla
# pickaxe (vanilla handheld angles). A flat card was tried for cleaner edges and reverted:
# nikoc wants the 3D thickness.
k = 1.3
write('models/item/key_to_city.json', {
    'parent': 'minecraft:item/handheld', 'textures': {'layer0': 'elytro:item/key_to_city'},
    'display': {
        'thirdperson_righthand': {'rotation': [0, -90, 55], 'translation': [0, 4, 0.5], 'scale': [0.85 * k] * 3},
        'thirdperson_lefthand': {'rotation': [0, 90, -55], 'translation': [0, 4, 0.5], 'scale': [0.85 * k] * 3},
        'firstperson_righthand': {'rotation': [0, -90, 25], 'translation': [1.13, 3.2, 1.13], 'scale': [0.68 * k] * 3},
        'firstperson_lefthand': {'rotation': [0, 90, -25], 'translation': [1.13, 3.2, 1.13], 'scale': [0.68 * k] * 3},
    }})

print('inventory icons written')
