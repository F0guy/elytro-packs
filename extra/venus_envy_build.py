"""Venus Envy - a hoe skin (rare farming-event drop). A huge Venus flytrap forms the blade.

  venus_envy       the hoe. A vine-wrapped stalk with a seed-pod pommel and two leaves; at the
                   top, the trap: two lobes hinged at the stalk, green outside, red inside with
                   pale trigger hairs, rimmed with pale teeth that interlock when it shuts.
                   Held, the jaws breathe (minecraft:time, random + wobble). Every snap is the
                   script's: custom_model_data string "bite" / "shut" (venus_envy.sk sets them
                   when it eats a crop, and now and then at rest), so its petals always match.
  venus_petal      a little tooth-shaped petal, flung from the jaws by display entities.

The model stands upright (like Kraken's Grasp): the display transforms are vanilla
item/handheld's, each turned a further -45 degrees about z.
Writes into ./assets/elytro. Usage (needs Pillow): python venus_envy_build.py [--preview DIR]
"""
import json
import math
import os
import sys

from PIL import Image, ImageDraw

HERE = os.path.dirname(os.path.abspath(__file__))
A = os.path.join(HERE, 'assets', 'elytro')
TEX = 'elytro:item/venus_envy'

PAL = {
    'green': (74, 140, 52), 'green_dk': (44, 96, 34), 'green_hi': (128, 184, 74),
    'red': (176, 34, 52), 'red_dk': (120, 18, 36),
    'tooth': (236, 228, 204), 'tooth_dk': (196, 184, 150),
    'bark': (92, 64, 40), 'bark_dk': (62, 42, 26), 'pod': (152, 170, 64),
}
NAMES = list(PAL)
INNER, OUTER = 'inner', 'outer'          # detailed 16x16 regions


def texture():
    im = Image.new('RGBA', (64, 64), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    for i, n in enumerate(NAMES):
        x = i * 4
        d.rectangle([x, 0, x + 3, 3], fill=PAL[n] + (255,))
    # inner of the trap: red, darker toward the hinge, pale trigger hairs
    inner = Image.new('RGBA', (16, 16), PAL['red'] + (255,))
    di = ImageDraw.Draw(inner)
    for y in range(16):
        k = 1 - 0.35 * (y / 15)
        di.line([(0, y), (15, y)], fill=tuple(int(c * k) for c in PAL['red']) + (255,))
    for x, y in ((4, 4), (11, 5), (7, 9), (3, 12), (12, 11)):
        di.point((x, y), fill=(250, 214, 200, 255))
    im.alpha_composite(inner, (32, 32))
    # outside: green with veins running out to the rim
    outer = Image.new('RGBA', (16, 16), PAL['green'] + (255,))
    do = ImageDraw.Draw(outer)
    for k in range(5):
        x0 = 1 + k * 3.5
        do.line([(8, 15), (x0, 0)], fill=PAL['green_dk'] + (255,))
    do.line([(0, 0), (15, 0)], fill=PAL['green_hi'] + (255,))
    im.alpha_composite(outer, (48, 32))
    return im


def uv_of(c):
    if c == INNER:
        return [8.25, 8.25, 11.75, 11.75]
    if c == OUTER:
        return [12.25, 8.25, 15.75, 11.75]
    i = NAMES.index(c)
    return [i + 0.25, 0.25, i + 0.75, 0.75]


FACES = ('north', 'south', 'east', 'west', 'up', 'down')


def box(frm, to, col, rot=None):
    f = {}
    for k in FACES:
        c = col if isinstance(col, str) else col.get(k, col.get('default'))
        f[k] = {'uv': uv_of(c), 'texture': '#0'}
    e = {'from': [round(v, 3) for v in frm], 'to': [round(v, 3) for v in to], 'faces': f, '_col': col}
    if rot:
        axis, angle, origin = rot
        e['rotation'] = {'axis': axis, 'angle': round(angle, 2), 'origin': [round(v, 3) for v in origin]}
    return e


HINGE = (8.0, 19.8)


def stalk():
    E = []
    G = {'default': 'green', 'up': 'green_hi'}
    E.append(box([6.9, -3.6, 6.9], [9.1, -1.4, 9.1], {'default': 'pod', 'down': 'green_dk'}))        # seed pod
    E.append(box([7.0, -1.6, 7.0], [9.0, 6.0, 9.0], {'default': 'bark'}))                              # grip
    for y in (0.0, 2.4, 4.8):                                                                         # vine wraps
        E.append(box([6.8, y, 6.8], [9.2, y + 0.7, 9.2], {'default': 'green_dk'}))
    E.append(box([7.2, 6.0, 7.2], [8.8, 18.0, 8.8], G))                                               # stalk
    E.append(box([6.6, 17.6, 6.6], [9.4, 19.4, 9.4], {'default': 'green', 'up': 'green_hi'}))        # node under the trap
    # two leaves sprouting off the stalk
    L = {'default': 'green_hi', 'down': 'green_dk'}
    E.append(box([8.6, 10.0, 6.6], [12.0, 10.5, 9.4], L, ('z', 22.5, [8.6, 10.3, 8.0])))
    E.append(box([12.0, 10.0, 7.2], [13.6, 10.5, 8.8], L, ('z', 22.5, [8.6, 10.3, 8.0])))
    E.append(box([4.0, 13.4, 6.6], [7.4, 13.9, 9.4], L, ('z', -22.5, [7.4, 13.7, 8.0])))
    E.append(box([2.4, 13.4, 7.2], [4.0, 13.9, 8.8], L, ('z', -22.5, [7.4, 13.7, 8.0])))
    return E


def lobe(upper, angle):
    """One half of the trap, lying flat from the hinge out along -x, then turned about z by
    `angle` (upper lobe opens with negative angles, lower with positive)."""
    hx, hy = HINGE
    E = []
    if upper:
        y0, y1 = hy, hy + 1.6
        col = {'default': OUTER, 'down': INNER, 'east': 'green_dk'}
        ry0, ry1 = y0 - 0.5, y0
    else:
        y0, y1 = hy - 1.6, hy
        col = {'default': OUTER, 'up': INNER, 'east': 'green_dk'}
        ry0, ry1 = y1, y1 + 0.5
    rot = ('z', angle, [hx, hy, 8.0])
    # a broad, rounded lobe: narrow at the hinge, widest in the middle, rounded at the tip
    segs = ((5.0, 8.0, 5.2, 10.8), (1.0, 5.0, 3.0, 13.0), (-3.5, 1.0, 2.2, 13.8), (-6.4, -3.5, 3.6, 12.4), (-7.6, -6.4, 5.6, 10.4))
    for x0, x1, z0, z1 in segs:
        E.append(box([x0, y0, z0], [x1, y1, z1], col, rot))
    # a green rim ridge round the edge, the inside cupped
    R = {'default': 'green_hi'}
    E.append(box([-6.4, ry0, 2.2], [1.0, ry1, 2.8], R, rot))
    E.append(box([-6.4, ry0, 13.2], [1.0, ry1, 13.8], R, rot))
    # teeth on the rim, pointing at the other lobe (offset half a step on the lower lobe so they
    # mesh when shut)
    off = 0 if upper else 0.9
    ty0, ty1 = (ry0 - 2.6, ry0) if upper else (ry1, ry1 + 2.6)
    T = {'default': 'tooth', 'down' if upper else 'up': 'tooth_dk'}
    for x in (-5.6, -3.8, -2.0, -0.2):
        for z in (2.3, 13.3):
            E.append(box([x + off, ty0, z], [x + off + 0.45, ty1, z + 0.45], T, rot))
    for z in (4.2, 6.1, 8.0, 9.9):
        z += off
        if z > 11.6:
            continue
        E.append(box([-7.5, ty0, z], [-7.05, ty1, z + 0.45], T, rot))
    return E


def head(theta):
    return lobe(True, -theta) + lobe(False, theta)


def display():
    # vanilla item/handheld, each turned a further -45 degrees about z (the model stands upright)
    return {
        'thirdperson_righthand': {'rotation': [0, -90, 10], 'translation': [0, 4, 0.5], 'scale': [0.85, 0.85, 0.85]},
        'thirdperson_lefthand': {'rotation': [0, 90, -100], 'translation': [0, 4, 0.5], 'scale': [0.85, 0.85, 0.85]},
        'firstperson_righthand': {'rotation': [0, -90, -20], 'translation': [1.13, 3.2, 1.13], 'scale': [0.68, 0.68, 0.68]},
        'firstperson_lefthand': {'rotation': [0, 90, -70], 'translation': [1.13, 3.2, 1.13], 'scale': [0.68, 0.68, 0.68]},
        'ground': {'rotation': [0, 0, -45], 'translation': [0, 2, 0], 'scale': [0.5, 0.5, 0.5]},
        'head': {'rotation': [0, 180, -45], 'translation': [0, 13, 7], 'scale': [1, 1, 1]},
        'fixed': {'rotation': [0, 180, -45], 'scale': [0.9, 0.9, 0.9]},
        'gui': {'rotation': [0, 0, -45], 'translation': [-1, -1, 0], 'scale': [0.62, 0.62, 0.62]},
    }


def model(E):
    return {
        'credit': 'Elytro - Venus Envy (venus_envy_build.py)',
        'textures': {'0': TEX, 'particle': TEX},
        'gui_light': 'front',
        'elements': [{k: v for k, v in e.items() if k != '_col'} for e in E],
        'display': display(),
    }


def check(E):
    for e in E:
        for v in e['from'] + e['to']:
            assert -16 <= v <= 32, e
        if 'rotation' in e:
            assert -45 <= e['rotation']['angle'] <= 45, e['rotation']


def petal():
    """A small tooth-shaped petal: pale, pink at the root, pointed."""
    S = 8
    big = Image.new('RGBA', (16 * S, 16 * S), (0, 0, 0, 0))
    d = ImageDraw.Draw(big)
    d.polygon([(8 * S, 1 * S), (11.5 * S, 9 * S), (10 * S, 14 * S), (6 * S, 14 * S), (4.5 * S, 9 * S)], fill=(240, 232, 210, 255))
    d.polygon([(6.5 * S, 11 * S), (9.5 * S, 11 * S), (10 * S, 14 * S), (6 * S, 14 * S)], fill=(222, 120, 140, 255))
    d.line([(8 * S, 3 * S), (8 * S, 11 * S)], fill=(214, 200, 168, 255), width=S)
    small = big.resize((16, 16), Image.LANCZOS)
    px = small.load()
    for y in range(16):
        for x in range(16):
            r, g, b, a = px[x, y]
            px[x, y] = (r, g, b, 255) if a > 110 else (0, 0, 0, 0)
    return small


# ------------------------------------------------------------------ preview
def preview(E, path, yaw=0, pitch=10, roll=-45, size=300):
    def rot(p, axis, ang, o):
        a = math.radians(ang)
        x, y, z = p[0] - o[0], p[1] - o[1], p[2] - o[2]
        c, s = math.cos(a), math.sin(a)
        if axis == 'x':
            y, z = y * c - z * s, y * s + z * c
        elif axis == 'y':
            x, z = x * c + z * s, -x * s + z * c
        else:
            x, y = x * c - y * s, x * s + y * c
        return (x + o[0], y + o[1], z + o[2])

    def view(p):
        x, y, z = p[0] - 8, p[1] - 8, p[2] - 8
        r = math.radians(roll)
        x, y = x * math.cos(r) - y * math.sin(r), x * math.sin(r) + y * math.cos(r)
        a = math.radians(yaw)
        x, z = x * math.cos(a) + z * math.sin(a), -x * math.sin(a) + z * math.cos(a)
        b = math.radians(pitch)
        y, z = y * math.cos(b) - z * math.sin(b), y * math.sin(b) + z * math.cos(b)
        k = size / 36
        return (size / 2 + x * k, size / 2 - y * k, z)

    cols = dict(PAL)
    cols[INNER] = (160, 30, 48)
    cols[OUTER] = (70, 132, 50)
    quads = []
    shade = {'north': 0.85, 'south': 0.85, 'east': 0.65, 'west': 0.65, 'up': 1.0, 'down': 0.55}
    for e in E:
        (x0, y0, z0), (x1, y1, z1) = e['from'], e['to']
        corners = {
            'north': [(x0, y0, z0), (x1, y0, z0), (x1, y1, z0), (x0, y1, z0)],
            'south': [(x0, y0, z1), (x1, y0, z1), (x1, y1, z1), (x0, y1, z1)],
            'west': [(x0, y0, z0), (x0, y0, z1), (x0, y1, z1), (x0, y1, z0)],
            'east': [(x1, y0, z0), (x1, y0, z1), (x1, y1, z1), (x1, y1, z0)],
            'up': [(x0, y1, z0), (x1, y1, z0), (x1, y1, z1), (x0, y1, z1)],
            'down': [(x0, y0, z0), (x1, y0, z0), (x1, y0, z1), (x0, y0, z1)],
        }
        col = e['_col']
        for f in FACES:
            pts = corners[f]
            if 'rotation' in e:
                r = e['rotation']
                pts = [rot(p, r['axis'], r['angle'], r['origin']) for p in pts]
            vp = [view(p) for p in pts]
            c = col if isinstance(col, str) else col.get(f, col.get('default'))
            rgb = cols[c]
            quads.append((sum(p[2] for p in vp) / 4, [(p[0], p[1]) for p in vp], tuple(int(v * shade[f]) for v in rgb)))
    im = Image.new('RGBA', (size, size), (70, 74, 82, 255))
    d = ImageDraw.Draw(im)
    for _, pts, c in sorted(quads, key=lambda q: -q[0]):
        d.polygon(pts, fill=c + (255,), outline=tuple(max(0, v - 25) for v in c) + (255,))
    im.save(path)


# ------------------------------------------------------------------ write
def write(rel, data):
    path = os.path.join(A, rel)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    if isinstance(data, Image.Image):
        data.save(path)
    else:
        with open(path, 'w', encoding='utf-8', newline='\n') as f:
            json.dump(data, f, separators=(',', ':'))


BREATH = 12          # idle poses, jaws easing between 30 and 42 degrees open
BITE, SHUT = 18, 3   # snap poses


def m(name):
    return {'type': 'minecraft:model', 'model': 'elytro:item/venus_envy/' + name}


def build(preview_dir=None):
    write('textures/item/venus_envy.png', texture())
    write('textures/item/venus_petal.png', petal())
    base = stalk()
    check(base)
    write('models/item/venus_envy/stalk.json', model(base))
    for i in range(BREATH):
        theta = 30 + 12 * (0.5 - 0.5 * math.cos(math.pi * i / (BREATH - 1)))
        E = head(theta)
        check(E)
        write('models/item/venus_envy/open_%02d.json' % i, model(E))
    for name, theta in (('bite', BITE), ('shut', SHUT)):
        E = head(theta)
        check(E)
        write('models/item/venus_envy/%s.json' % name, model(E))
    write('models/item/venus_petal.json', {'parent': 'minecraft:item/generated', 'textures': {'layer0': 'elytro:item/venus_petal'}})
    write('items/venus_petal.json', {'model': {'type': 'minecraft:model', 'model': 'elytro:item/venus_petal'}})
    # idle: the random wobble hovers mid-range (breathing); its rare far swings are a snap
    # (snaps are all the script's, so the petals it throws always match them)
    entries = [{'threshold': round(0.25 + 0.5 * i / BREATH, 4), 'model': m('open_%02d' % i)} for i in range(BREATH)]
    entries[0]['threshold'] = 0.0
    idle = {'type': 'minecraft:range_dispatch', 'property': 'minecraft:time', 'source': 'random', 'wobble': True, 'entries': entries}
    jaws = {'type': 'minecraft:select', 'property': 'minecraft:custom_model_data', 'index': 0,
            'cases': [{'when': 'bite', 'model': m('bite')}, {'when': 'shut', 'model': m('shut')}],
            'fallback': idle}
    write('items/venus_envy.json', {
        'hand_animation_on_swap': False,
        'model': {'type': 'minecraft:select', 'property': 'minecraft:display_context',
                  'cases': [{'when': ['gui', 'fixed'], 'model': {'type': 'minecraft:composite', 'models': [m('stalk'), m('open_06')]}}],
                  'fallback': {'type': 'minecraft:composite', 'models': [m('stalk'), jaws]}}})
    if preview_dir:
        for name, theta in (('open', 36), ('bite', BITE), ('shut', SHUT)):
            preview(base + head(theta), os.path.join(preview_dir, 'venus_%s.png' % name))
            preview(base + head(theta), os.path.join(preview_dir, 'venus_%s_side.png' % name), yaw=55, roll=0)
    print('Venus Envy: stalk %d + jaws %d elements, %d breathing poses + bite/shut' % (len(base), len(head(36)), BREATH))


if __name__ == '__main__':
    out = None
    if '--preview' in sys.argv:
        out = sys.argv[sys.argv.index('--preview') + 1]
        os.makedirs(out, exist_ok=True)
    build(out)
