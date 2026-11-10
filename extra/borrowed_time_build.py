"""Borrowed Time - a sword skin (reward for reaching #1 on /leveltop).

The blade is an hourglass in a brass frame, pinned at its waist between two tines that rise from
a clockwork guard. Its sand runs the wrong way, from the hilt end up into the tip end (borrowed
time runs backwards). When the last grain has gone up, the whole glass flips over on its pin and
the sand starts climbing again.

Animated by pose gating (gated_model.py): the hourglass is posed 64 times on one animated
texture; 40 poses of pouring (5 ticks each, about 10 s) and 24 of the flip (eased, about 1.6 s).

Writes into ./assets/elytro (this folder):
  items/borrowed_time.json
  models/item/borrowed_time.json, borrowed_time_icon.json
  textures/item/borrowed_time.png, borrowed_time_glass.png (+ .mcmeta), borrowed_time_icon.png
Usage (needs Pillow): python borrowed_time_build.py [--preview DIR]
"""
import json
import math
import os
import random
import sys

from PIL import Image, ImageDraw

from gated_model import hand_display, Gated, Swatches, mix, outline, check, strip_names

HERE = os.path.dirname(os.path.abspath(__file__))
A = os.path.join(HERE, 'assets', 'elytro')

POUR, FLIP = 40, 24
POUR_TICKS = 5

BRASS = (214, 160, 70)
BRASS_LIGHT = (255, 214, 130)
BRASS_DARK = (122, 82, 34)
WOOD = (88, 52, 34)
WOOD_DARK = (52, 30, 20)
LEATHER = (60, 34, 30)
SAND = (236, 196, 110)
SAND_LIGHT = (255, 236, 170)
GLASS = (200, 236, 245)
FACE = (240, 230, 206)

S = Swatches('#0', {'brass': (0, 0), 'brass_dark': (1, 0), 'brass_light': (2, 0), 'leather': (3, 0),
                    'wood': (4, 0), 'wood_dark': (5, 0), 'face': (6, 0), 'gear': (7, 0)})
G = Gated('glass', '#1', POUR + FLIP, POUR_TICKS, {
    'sand': (SAND, SAND_LIGHT), 'stream': (SAND_LIGHT, (255, 250, 220)),
    'brass': (BRASS, BRASS_LIGHT), 'brass_dark': (BRASS_DARK, BRASS),
    'glass': (GLASS, (240, 252, 255), 92)})


def ease(t):
    return t * t * (3 - 2 * t)


# pour poses hold POUR_TICKS each; flip poses are short, slow at both ends of the turn
G.durations = [POUR_TICKS] * POUR + [2 if i in (0, 1, FLIP - 2, FLIP - 1) else 1 for i in range(FLIP)]


def static_texture():
    rnd = random.Random(5)
    im = Image.new('RGBA', (64, 64), (0, 0, 0, 0))
    px = im.load()

    def fill(name, fn):
        cx, cy = S.layout[name]
        for y in range(8):
            for x in range(8):
                px[cx * 8 + x, cy * 8 + y] = fn(x, y, rnd.random())

    fill('brass', lambda x, y, n: mix(BRASS, BRASS_LIGHT, (1 - y / 7) * 0.5 + 0.3 * n))
    fill('brass_dark', lambda x, y, n: mix(BRASS_DARK, BRASS, 0.4 * n))
    fill('brass_light', lambda x, y, n: mix(BRASS_LIGHT, (255, 240, 200), 0.5 * n))
    fill('leather', lambda x, y, n: mix((34, 18, 16), LEATHER, 0.9 if (x + 2 * y) % 4 else 0.3))
    fill('wood', lambda x, y, n: mix(WOOD_DARK, WOOD, 0.55 + 0.35 * math.sin(x * 1.3 + n)))
    fill('wood_dark', lambda x, y, n: mix(WOOD_DARK, WOOD, 0.3 * n))

    def face(x, y, n):
        # a clock face: cream with a brass rim and two dark hands
        r = math.hypot(x - 3.5, y - 3.5)
        if r > 3.6:
            return BRASS_DARK + (255,)
        if (x, y) in ((3, 1), (3, 2), (3, 3), (4, 3), (5, 3), (4, 4)):
            return (30, 22, 20, 255)
        return mix(FACE, (255, 250, 236), 0.3 * n)
    fill('face', face)

    def gear(x, y, n):
        r = math.hypot(x - 3.5, y - 3.5)
        tooth = (x + y) % 2 == 0 and r > 2.8
        return (BRASS_DARK + (255,)) if r < 1.2 else mix(BRASS, BRASS_LIGHT, 0.7 if tooth else 0.3)
    fill('gear', gear)
    return im


# ---------------------------------------------------------------- the sword (static)
WAIST = (8.0, 14.7, 8.0)
HALF = 11.0          # waist to each end cap


def sword():
    E = []
    b = S.box
    E.append(b([6.9, -13.8, 6.9], [9.1, -12.4, 9.1], 'brass', name='pommel'))
    E.append(b([7.4, -14.4, 7.4], [8.6, -13.8, 8.6], 'brass_light', name='pommel cap'))
    E.append(b([7.3, -12.4, 7.3], [8.7, -2.6, 8.7], 'leather', name='grip'))
    for y in (-10.3, -7.5, -4.7):
        E.append(b([7.15, y - 0.25, 7.15], [8.85, y + 0.25, 8.85], 'brass_dark', name='grip band'))
    # guard: a brass bar with a clock face on each side and small gears at the ends
    E.append(b([4.0, -2.6, 7.0], [12.0, -0.8, 9.0], 'brass', faces_mat={'down': 'brass_dark'}, name='guard'))
    E.append(b([6.2, -3.4, 6.6], [9.8, 0.2, 9.4], 'brass_dark', name='guard hub'))
    E.append(b([6.5, -3.1, 9.4], [9.5, -0.1, 9.55], 'face', name='clock face S'))
    E.append(b([6.5, -3.1, 6.45], [9.5, -0.1, 6.6], 'face', name='clock face N'))
    for x in (2.6, 13.4):
        E.append(b([x - 1.3, -3.0, 7.3], [x + 1.3, -0.4, 8.7], 'gear', name='guard gear'))
    # the fork: two tines up the front and back to the pin at the hourglass waist
    for z0, z1 in ((9.7, 10.2), (5.8, 6.3)):
        E.append(b([7.7, 0.2, z0], [8.3, WAIST[1] + 0.3, z1], 'brass', faces_mat={'up': 'brass_light'}, name='tine'))
    E.append(b([7.55, WAIST[1] - 0.45, 5.6], [8.45, WAIST[1] + 0.45, 10.4], 'brass_light', name='pin'))
    return E


# ---------------------------------------------------------------- the hourglass (gated)
def sand_level(pose):
    """1 = all the sand in the hilt-end bulb, 0 = all of it in the tip end."""
    if pose >= POUR:
        return 0.0
    return 1 - ease(pose / (POUR - 1))


def flip_angle(pose):
    if pose < POUR:
        return 0.0
    t = (pose - POUR + 1) / FLIP
    return 180 * ease(t)


def hourglass(pose):
    """Everything turns with the glass. During the flip the sand stays put in the glass, so after
    180 degrees the full bulb is at the hilt end again: the same picture as pose 0."""
    ang = flip_angle(pose)
    s = sand_level(pose)
    sand, glass, frame = [], [], []
    C = WAIST

    def add(lst, local, half, mat, light=0, cull=()):
        lst.append(G.box(pose, C, local, half, ang, {'all': mat}, light=light, cull=cull))

    # sand clings to the tip-ward end of each bulb (it falls toward the tip): the hilt-end bulb
    # (local -y) empties from its far end up to the neck, the tip-end bulb fills from its cap down
    wide = 7.2                       # inner height of a bulb's wide part (local 3.0 .. 10.2)
    if s > 0.04:
        h = wide * s
        add(sand, (0, -3.0 - h / 2, 0), (1.3, h / 2, 1.0), 'sand', light=4)
        add(sand, (0, -2.35, 0), (1.0, 0.82, 0.8), 'sand', light=4, cull=('up', 'down'))
        add(sand, (0, -1.0, 0), (0.5, 0.46, 0.42), 'sand', light=4, cull=('up', 'down'))
    if s < 0.98:
        h = wide * (1 - s)
        add(sand, (0, 10.2 - h / 2, 0), (1.3, h / 2, 1.0), 'sand', light=4)
        if s > 0.04 and pose < POUR:
            top = 10.2 - h
            add(sand, (0, (-0.6 + top) / 2, 0), (0.13, (top + 0.6) / 2, 0.13), 'stream', light=10)
    # brass end caps (with a point beyond each) and two side rails
    for sy in (-1, 1):
        add(frame, (0, sy * (HALF - 0.45), 0), (2.6, 0.45, 1.65), 'brass')
        add(frame, (0, sy * (HALF + 0.35), 0), (1.6, 0.35, 1.1), 'brass_dark')
        add(frame, (0, sy * (HALF + 1.15), 0), (0.75, 0.5, 0.6), 'brass')
    for sx in (-1, 1):
        add(frame, (sx * 2.3, 0, 0), (0.28, HALF - 0.9, 0.28), 'brass_dark', cull=('up', 'down'))
    # the glass: two stepped bulbs and a narrow neck
    for sy in (-1, 1):
        # each bulb swells out in the middle and narrows toward its cap and the neck
        add(glass, (0, sy * 9.45, 0), (1.45, 0.75, 1.1), 'glass', cull=('up', 'down'))
        add(glass, (0, sy * 6.5, 0), (2.05, 2.2, 1.45), 'glass')
        add(glass, (0, sy * 3.75, 0), (1.55, 0.55, 1.15), 'glass', cull=('up', 'down'))
        add(glass, (0, sy * 2.35, 0), (1.15, 0.85, 0.95), 'glass', cull=('up', 'down'))
        add(glass, (0, sy * 1.0, 0), (0.7, 0.5, 0.6), 'glass', cull=('up', 'down'))
    add(glass, (0, 0, 0), (0.32, 0.5, 0.32), 'glass', cull=('up', 'down'))
    # sand first, then the opaque frame, the see-through glass last (items draw in this order)
    return sand + frame + glass


DISPLAY = {
    'gui': {'rotation': [12, -24, -37], 'translation': [0, 0, 0], 'scale': [0.51, 0.51, 0.51]},
    'firstperson_righthand': {'rotation': [0, -90, 22], 'translation': [1, -1, -1.7], 'scale': [0.67, 0.67, 0.67]},
    'firstperson_lefthand': {'rotation': [0, 90, -22], 'translation': [1, -1, -1.7], 'scale': [0.67, 0.67, 0.67]},
    'thirdperson_righthand': {'rotation': [0, 90, -18], 'translation': [0, 2, 0], 'scale': [0.63, 0.63, 0.63]},
    'thirdperson_lefthand': {'rotation': [0, -90, 18], 'translation': [0, 2, 0], 'scale': [0.63, 0.63, 0.63]},
    'ground': {'rotation': [0, 0, -25], 'translation': [0, 3, 0], 'scale': [0.35, 0.35, 0.35]},
    'fixed': {'rotation': [0, 180, -35], 'translation': [0, 0, 0], 'scale': [0.48, 0.48, 0.48]},
    'head': {'rotation': [0, 180, 0], 'translation': [0, 6, 0], 'scale': [0.6, 0.6, 0.6]},
}
# Held by the grip: vanilla's sword transforms, fitted so the grip sits where vanilla's handle does
DISPLAY.update(hand_display('sword', -7.3))


def icon():
    """32x32 drawn at size: hilt bottom-left, the hourglass blade on the diagonal, sand gathered
    at its tip end."""
    im = Image.new('RGBA', (32, 32), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    br, bl, bd = BRASS + (255,), BRASS_LIGHT + (255,), BRASS_DARK + (255,)
    gl, gs = (210, 240, 248, 255), (170, 210, 226, 255)
    sd, sl = SAND + (255,), SAND_LIGHT + (255,)
    lea = LEATHER + (255,)
    for i in range(5):
        d.point([(4 + i, 27 - i), (5 + i, 27 - i), (4 + i, 26 - i)], fill=lea)
    d.point([(5, 26), (7, 24)], fill=bd)
    d.rectangle([2, 28, 3, 29], fill=br)
    for i in range(7):
        d.point([(6 + i, 19 + i), (7 + i, 19 + i)], fill=br if i != 3 else bd)
    d.rectangle([9, 21, 10, 23], fill=(240, 230, 206, 255))
    d.point([(9, 22)], fill=(30, 22, 20, 255))
    # hourglass along the diagonal from (12,19) to (27,4): two bulbs, waist at (19.5,11.5)
    def bulb(cx, cy, r, fill):
        for dx in range(-r, r + 1):
            for dy in range(-r, r + 1):
                if abs(dx) + abs(dy) <= r + 1 and abs(dx - dy) <= r * 2 - 1:
                    d.point([(cx + dx, cy + dy)], fill=fill)
    bulb(15, 16, 2, gl)
    bulb(23, 8, 2, gl)
    d.point([(19, 12), (20, 11)], fill=gs)
    bulb(24, 7, 1, sd)
    d.point([(23, 7), (24, 8), (22, 8), (24, 6)], fill=sl)
    d.point([(16, 16), (15, 17)], fill=sd)
    d.line([(17, 14), (22, 9)], fill=sl)
    for (x, y) in ((11, 18), (12, 19), (12, 18), (26, 4), (27, 5), (27, 4)):
        d.point([(x, y)], fill=br)
    d.point([(28, 3), (10, 20)], fill=bl)
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
    static = sword()
    gated = [e for p in range(G.poses) for e in hourglass(p)]
    E = static + gated
    check(E)
    write('models/item/borrowed_time.json', {
        'credit': 'Elytro - Borrowed Time (borrowed_time_build.py)',
        'textures': {'0': 'elytro:item/borrowed_time', '1': 'elytro:item/borrowed_time_glass', 'particle': 'elytro:item/borrowed_time'},
        'gui_light': 'front', 'display': DISPLAY, 'elements': strip_names(E)})
    write('textures/item/borrowed_time.png', static_texture())
    write('textures/item/borrowed_time_glass.png', G.texture())
    write('textures/item/borrowed_time_glass.png.mcmeta', G.mcmeta())
    write('textures/item/borrowed_time_icon.png', icon())
    write('models/item/borrowed_time_icon.json', {'parent': 'minecraft:item/generated', 'textures': {'layer0': 'elytro:item/borrowed_time_icon'}})
    write('items/borrowed_time.json', {
        'hand_animation_on_swap': False,
        'model': {'type': 'minecraft:select', 'property': 'minecraft:display_context',
                  'cases': [{'when': ['gui', 'fixed'], 'model': {'type': 'minecraft:model', 'model': 'elytro:item/borrowed_time_icon'}}],
                  'fallback': {'type': 'minecraft:model', 'model': 'elytro:item/borrowed_time'}}})
    print('Borrowed Time: %d static + %d hourglass elements (%d poses, cycle %d ticks)' % (
        len(static), len(gated), G.poses, sum(G.durations)))
    if preview_dir:
        os.makedirs(preview_dir, exist_ok=True)
        write('bt_static.png', static_texture(), preview_dir)
        write('bt_glass_all.png', G.opaque(), preview_dir)
        write('bt_icon.png', icon().resize((256, 256), Image.NEAREST), preview_dir)
        # the preview renderer steps poses by a fixed tick count; give it per-pose start ticks
        starts, t = [], 0
        for dur in G.durations:
            starts.append(t)
            t += dur
        write('bt_elements.json', {'glass_poses': G.poses, 'glass_ticks': POUR_TICKS, 'glass_starts': starts,
                                   'textures': {'#0': 'bt_static.png', '#1': 'bt_glass_all.png'},
                                   'elements': E}, preview_dir)


if __name__ == '__main__':
    build(sys.argv[sys.argv.index('--preview') + 1] if '--preview' in sys.argv else None)
