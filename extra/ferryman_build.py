"""The Ferryman - a fishing rod skin (reward for reaching #1 on /fish coins top).

The rod is a ferryman's oar: a weathered pole, its paddle blade below the hand, rope wound round
the grip, two bronze line guides, and at the top a crook from which a lantern of pale green ghost
fire swings, steadily, back and forth. The bobber is an old coin (the fare) floating flat on the
water, and the line is a rope.

The lantern swings by pose gating (gated_model.py): 24 poses, 3 ticks each, one swing in 3.6 s.
The flame flickers because each pose's flame cell is painted a little brighter or dimmer.

FishingCore draws the line and bobber (rod-cosmetics.ferryman in its config), using:
  elytro:ferryman_line    one segment of rope (+z, one block)
  elytro:ferryman_bobber  the coin

Writes into ./assets/elytro (this folder):
  items/ferryman.json, items/ferryman_line.json, items/ferryman_bobber.json
  models/item/ferryman.json, ferryman_icon.json, ferryman_line.json, ferryman_bobber.json
  textures/item/ferryman.png, ferryman_lantern.png (+ .mcmeta), ferryman_icon.png,
  ferryman_coin.png, ferryman_line.png
Usage (needs Pillow): python ferryman_build.py [--preview DIR]
"""
import json
import math
import os
import random
import sys

from PIL import Image, ImageDraw

from gated_model import Gated, Swatches, FACES, mix, outline, check, strip_names, rnd3

HERE = os.path.dirname(os.path.abspath(__file__))
A = os.path.join(HERE, 'assets', 'elytro')
SWING = 24
SWING_TICKS = 3

WOOD = (98, 74, 54)
WOOD_DARK = (54, 40, 32)
WOOD_PALE = (140, 116, 88)
ROPE = (170, 140, 96)
ROPE_DARK = (110, 86, 56)
BRONZE = (150, 110, 60)
BRONZE_DARK = (82, 60, 34)
VERDIGRIS = (96, 150, 128)
FIRE = (120, 255, 200)
FIRE_CORE = (220, 255, 240)
GLASS = (170, 230, 210)
GOLD = (222, 176, 76)
GOLD_DARK = (140, 98, 36)

S = Swatches('#0', {'wood': (0, 0), 'wood_dark': (1, 0), 'wood_pale': (2, 0), 'rope': (3, 0),
                    'bronze': (4, 0), 'bronze_dark': (5, 0), 'iron': (6, 0), 'verdigris': (7, 0)})
G = Gated('lantern', '#1', SWING, SWING_TICKS, {
    'fire': (FIRE, FIRE_CORE), 'bronze': (BRONZE, (196, 150, 90)), 'bronze_dark': (BRONZE_DARK, BRONZE),
    'chain': ((70, 66, 62), (120, 114, 104)), 'glass': (GLASS, (220, 255, 240), 88)})


def flicker(pose, name, cols):
    if name != 'fire':
        return cols
    k = 0.78 + 0.22 * math.sin(pose * 2.3) * math.sin(pose * 0.9 + 1)
    lo, hi = cols
    return tuple(int(c * k) for c in lo), tuple(min(255, int(c * (0.9 + 0.1 * k))) for c in hi)


G.vary = flicker


def static_texture():
    rnd = random.Random(12)
    im = Image.new('RGBA', (64, 64), (0, 0, 0, 0))
    px = im.load()
    grain = [rnd.random() for _ in range(8)]

    def fill(name, fn):
        cx, cy = S.layout[name]
        for y in range(8):
            for x in range(8):
                px[cx * 8 + x, cy * 8 + y] = fn(x, y, rnd.random())

    fill('wood', lambda x, y, n: mix(WOOD_DARK, WOOD, 0.45 + 0.4 * grain[x] + 0.15 * n))
    fill('wood_dark', lambda x, y, n: mix(WOOD_DARK, WOOD, 0.25 * n))
    fill('wood_pale', lambda x, y, n: mix(WOOD, WOOD_PALE, 0.4 + 0.5 * grain[(x + y) % 8]))
    fill('rope', lambda x, y, n: mix(ROPE_DARK, ROPE, 0.9 if (x + y) % 3 else 0.2))
    fill('bronze', lambda x, y, n: mix(BRONZE, (196, 150, 90), (1 - y / 7) * 0.5 + 0.2 * n) if n > 0.18 else mix(VERDIGRIS, (140, 190, 168), n))
    fill('bronze_dark', lambda x, y, n: mix(BRONZE_DARK, BRONZE, 0.4 * n))
    fill('iron', lambda x, y, n: mix((52, 50, 54), (98, 96, 100), 0.5 * n))
    fill('verdigris', lambda x, y, n: mix(VERDIGRIS, (150, 200, 176), n))
    return im


def seg(p, q, w, mat, faces_mat=None):
    """A square-section box from p to q in the x-y plane (z = 8), turned with one z rotation."""
    (x1, y1), (x2, y2) = p, q
    da, db = x2 - x1, y2 - y1
    length = math.hypot(da, db) + 0.3
    ang = math.degrees(math.atan2(db, da))
    k = round(ang / 90)
    turn = ang - 90 * k
    la, lb = (length, w) if k % 2 == 0 else (w, length)
    cx, cy = (x1 + x2) / 2, (y1 + y2) / 2
    rot = {'angle': round(turn, 3), 'axis': 'z', 'origin': rnd3([cx, cy, 8])} if abs(turn) > 0.3 else None
    return S.box([cx - la / 2, cy - lb / 2, 8 - w / 2], [cx + la / 2, cy + lb / 2, 8 + w / 2], mat, rot=rot, faces_mat=faces_mat)


HOOK = (12.7, 18.2)


def oar():
    E = []
    b = S.box
    # the paddle blade below the hand, an iron band where it meets the pole
    E.append(b([6.3, -14.4, 7.65], [9.7, -9.9, 8.35], 'wood_pale', faces_mat={'east': 'wood_dark', 'west': 'wood_dark'}, name='blade'))
    E.append(b([6.8, -15.4, 7.7], [9.2, -14.4, 8.3], 'wood_pale', name='blade tip'))
    E.append(b([7.6, -14.2, 7.55], [8.4, -10.0, 8.45], 'wood', name='blade spine'))
    E.append(b([7.2, -10.3, 7.2], [8.8, -9.5, 8.8], 'iron', name='band'))
    # the pole, rope wound round the grip, two line guides
    E.append(b([7.4, -9.5, 7.4], [8.6, 17.4, 8.6], 'wood', faces_mat={'up': 'wood_dark'}, name='pole'))
    E.append(b([7.2, -8.6, 7.2], [8.8, -1.6, 8.8], 'rope', name='rope grip'))
    for y in (-8.8, -1.4):
        E.append(b([7.1, y - 0.25, 7.1], [8.9, y + 0.25, 8.9], 'rope', name='rope knot'))
    for y in (5.5, 12.0):
        E.append(b([8.6, y - 0.4, 7.75], [9.5, y + 0.4, 8.25], 'bronze', name='guide'))
        E.append(b([9.5, y - 0.15, 7.8], [9.9, y + 0.55, 8.2], 'bronze_dark', name='guide ring'))
    # the crook: up, over, and down to the hook the lantern hangs from
    pts = [(8.0, 17.0), (8.4, 19.0), (9.6, 20.4), (11.2, 20.9), (12.5, 20.2), (12.9, 19.0)]
    for p, q in zip(pts, pts[1:]):
        E.append(seg(p, q, 1.05, 'wood'))
    E.append(S.box([12.4, 18.0, 7.6], [13.2, 18.9, 8.4], 'bronze_dark', name='hook'))
    return E


def lantern(pose):
    ang = 12 * math.sin(math.tau * pose / SWING)
    C = (HOOK[0], HOOK[1], 8.0)
    fire, solid, glass = [], [], []

    k = 1.3   # lantern scale

    def add(lst, local, half, mat, light=0, cull=()):
        lst.append(G.box(pose, C, tuple(v * k for v in local), tuple(v * k for v in half), ang,
                         {'all': mat}, light=light, cull=cull))

    add(fire, (0, -3.75, 0), (0.36, 0.75, 0.36), 'fire', light=15)
    add(fire, (0, -3.05, 0), (0.18, 0.3, 0.18), 'fire', light=15)
    add(solid, (0, -0.7, 0), (0.12, 0.7, 0.12), 'chain')
    add(solid, (0, -1.6, 0), (0.45, 0.22, 0.45), 'bronze')
    add(solid, (0, -2.05, 0), (1.15, 0.25, 1.15), 'bronze_dark')
    for sx in (-1, 1):
        for sz in (-1, 1):
            add(solid, (sx * 0.95, -3.65, sz * 0.95), (0.15, 1.38, 0.15), 'bronze', cull=('up', 'down'))
    add(solid, (0, -5.2, 0), (1.05, 0.25, 1.05), 'bronze_dark')
    add(glass, (0, -3.65, 0), (0.86, 1.36, 0.86), 'glass', cull=('up', 'down'))
    return fire + solid + glass


def rod_display():
    # Kraken's Grasp's (verified in game): handheld_rod's transforms turned a further -45 about z
    return {
        'thirdperson_righthand': {'rotation': [0, 90, 10], 'translation': [0, 4, 2.5], 'scale': [0.85, 0.85, 0.85]},
        'thirdperson_lefthand': {'rotation': [0, -90, -100], 'translation': [0, 4, 2.5], 'scale': [0.85, 0.85, 0.85]},
        'firstperson_righthand': {'rotation': [0, 90, -20], 'translation': [0, 1.6, 0.8], 'scale': [0.68, 0.68, 0.68]},
        'firstperson_lefthand': {'rotation': [0, -90, -70], 'translation': [0, 1.6, 0.8], 'scale': [0.68, 0.68, 0.68]},
        'ground': {'rotation': [0, 0, -45], 'translation': [0, 2, 0], 'scale': [0.5, 0.5, 0.5]},
        'head': {'rotation': [0, 180, -45], 'translation': [0, 13, 7], 'scale': [1, 1, 1]},
        'fixed': {'rotation': [0, 180, -45], 'scale': [1, 1, 1]},
        'gui': {'rotation': [0, 0, -45], 'scale': [0.58, 0.58, 0.58]},
    }


# ---------------------------------------------------------------- coin bobber and rope line
def coin_texture():
    """16x16: a worn gold coin, a skull struck into it."""
    im = Image.new('RGBA', (16, 16), (0, 0, 0, 0))
    px = im.load()
    rnd = random.Random(3)
    skull = ['..XXXX..',
             '.XXXXXX.',
             'XXXXXXXX',
             'X..XX..X',
             'X..XX..X',
             'XXXX.XXX',
             '.XXXXXX.',
             '..X.X.X.']
    for y in range(16):
        for x in range(16):
            r = math.hypot(x - 7.5, y - 7.5)
            if r > 8.2:
                continue
            c = mix(GOLD, (255, 222, 140), 0.3 + 0.3 * rnd.random() - 0.04 * (y - 7.5))
            if r > 6.6:
                c = mix(GOLD_DARK, GOLD, 0.4)
            sx, sy = x - 4, y - 4
            if 0 <= sx < 8 and 0 <= sy < 8:
                ch = skull[sy][sx]
                if ch == 'X':
                    c = mix((255, 232, 160), (255, 246, 210), rnd.random())
                elif ch == '.' and 2 <= sy <= 5:
                    c = mix(GOLD_DARK, (100, 66, 22), 0.5)
            px[x, y] = c
    return im


def coin_model():
    """A flat coin centred on (8, 8, 8), lying on the water: an octagon of three boxes, the coin
    image mapped across their tops and bottoms so it reads as one round face."""
    R = 2.6
    boxes = [(R, R * 0.6), (R * 0.6, R), (R * 0.86, R * 0.86)]
    E = []
    for hx, hz in boxes:
        x0, x1, z0, z1 = 8 - hx, 8 + hx, 8 - hz, 8 + hz

        def u(x):
            return round((x - (8 - R)) / (2 * R) * 16, 3)

        def v(z):
            return round((z - (8 - R)) / (2 * R) * 16, 3)
        rim = [0.2, 7.6, 0.6, 8.0]
        faces = {'up': {'uv': [u(x0), v(z0), u(x1), v(z1)], 'texture': '#0'},
                 'down': {'uv': [u(x0), v(z1), u(x1), v(z0)], 'texture': '#0'}}
        for f in ('north', 'south', 'east', 'west'):
            faces[f] = {'uv': rim, 'texture': '#0'}
        E.append({'from': rnd3([x0, 7.6, z0]), 'to': rnd3([x1, 8.4, z1]), 'faces': faces})
    return {'credit': 'Elytro - The Ferryman coin (ferryman_build.py)',
            'textures': {'0': 'elytro:item/ferryman_coin', 'particle': 'elytro:item/ferryman_coin'}, 'elements': E}


def line_texture():
    im = Image.new('RGBA', (16, 16), (0, 0, 0, 0))
    px = im.load()
    for y in range(16):
        for x in range(16):
            twist = (x + y) % 6
            px[x, y] = mix(ROPE_DARK, ROPE, 0.25 if twist == 0 else 0.6 + 0.08 * twist)
    return im


def line_model():
    faces = {f: {'uv': [0, 0, 16, 16], 'texture': '#0'} for f in FACES}
    return {'credit': 'Elytro - The Ferryman line (ferryman_build.py)',
            'textures': {'0': 'elytro:item/ferryman_line', 'particle': 'elytro:item/ferryman_line'},
            'elements': [{'from': [7.5, 7.5, 8], 'to': [8.5, 8.5, 24], 'faces': faces}]}


def icon():
    im = Image.new('RGBA', (32, 32), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    wd, wl, wk = WOOD + (255,), WOOD_PALE + (255,), WOOD_DARK + (255,)
    rp = ROPE + (255,)
    # the paddle blade at the bottom-left
    d.polygon([(1, 30), (1, 26), (5, 22), (9, 26), (5, 30)], fill=wl)
    d.line([(2, 29), (6, 25)], fill=wd)
    # pole on the diagonal, rope on the grip
    for i in range(18):
        x, y = 7 + i, 24 - i
        d.point([(x, y), (x + 1, y)], fill=wd)
        d.point([(x + 1, y + 1)], fill=wk)
    for i in (2, 4, 6):
        d.point([(7 + i, 24 - i), (8 + i, 24 - i)], fill=rp)
    # crook bending over to the right, the lantern hanging off it
    d.point([(25, 6), (26, 5), (27, 5), (28, 6), (29, 7)], fill=wd)
    d.point([(26, 4), (27, 4)], fill=wl)
    d.line([(29, 8), (29, 9)], fill=(90, 86, 80, 255))
    d.rectangle([27, 10, 31, 10], fill=BRONZE_DARK + (255,))
    d.rectangle([27, 11, 31, 14], fill=GLASS + (255,))
    d.rectangle([28, 11, 30, 14], fill=FIRE + (255,))
    d.point([(29, 12), (29, 13)], fill=FIRE_CORE + (255,))
    d.rectangle([27, 15, 31, 15], fill=BRONZE_DARK + (255,))
    return outline(im)


def write(rel, data, root=A):
    path = os.path.join(root, rel)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    if isinstance(data, Image.Image):
        data.save(path)
    else:
        with open(path, 'w', encoding='utf-8', newline='\n') as f:
            json.dump(data, f, separators=(',', ':'))


def build(preview_dir=None):
    static = oar()
    gated = [e for p in range(SWING) for e in lantern(p)]
    E = static + gated
    check(E)
    write('models/item/ferryman.json', {
        'credit': 'Elytro - The Ferryman (ferryman_build.py)',
        'textures': {'0': 'elytro:item/ferryman', '1': 'elytro:item/ferryman_lantern', 'particle': 'elytro:item/ferryman'},
        'gui_light': 'front', 'display': rod_display(), 'elements': strip_names(E)})
    write('textures/item/ferryman.png', static_texture())
    write('textures/item/ferryman_lantern.png', G.texture())
    write('textures/item/ferryman_lantern.png.mcmeta', G.mcmeta())
    write('textures/item/ferryman_icon.png', icon())
    write('textures/item/ferryman_coin.png', coin_texture())
    write('textures/item/ferryman_line.png', line_texture())
    write('models/item/ferryman_icon.json', {'parent': 'minecraft:item/generated', 'textures': {'layer0': 'elytro:item/ferryman_icon'}})
    write('models/item/ferryman_bobber.json', coin_model())
    write('models/item/ferryman_line.json', line_model())
    write('items/ferryman.json', {
        'hand_animation_on_swap': False,
        'model': {'type': 'minecraft:select', 'property': 'minecraft:display_context',
                  'cases': [{'when': ['gui', 'fixed'], 'model': {'type': 'minecraft:model', 'model': 'elytro:item/ferryman_icon'}}],
                  'fallback': {'type': 'minecraft:model', 'model': 'elytro:item/ferryman'}}})
    write('items/ferryman_bobber.json', {'model': {'type': 'minecraft:model', 'model': 'elytro:item/ferryman_bobber'}})
    write('items/ferryman_line.json', {'model': {'type': 'minecraft:model', 'model': 'elytro:item/ferryman_line'}})
    print('Ferryman: %d static + %d lantern elements (%d poses)' % (len(static), len(gated), SWING))
    if preview_dir:
        os.makedirs(preview_dir, exist_ok=True)
        write('fm_static.png', static_texture(), preview_dir)
        write('fm_lantern_all.png', G.opaque(), preview_dir)
        write('fm_icon.png', icon().resize((256, 256), Image.NEAREST), preview_dir)
        write('fm_coin.png', coin_texture().resize((128, 128), Image.NEAREST), preview_dir)
        write('fm_elements.json', {'lantern_poses': SWING, 'lantern_ticks': SWING_TICKS, 'centre': (8, -8, 3), 'ortho': 40,
                                   'textures': {'#0': 'fm_static.png', '#1': 'fm_lantern_all.png'}, 'elements': E}, preview_dir)


if __name__ == '__main__':
    build(sys.argv[sys.argv.index('--preview') + 1] if '--preview' in sys.argv else None)
