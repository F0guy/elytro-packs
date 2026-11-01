"""Sandevistan - a cosmetic chestplate skin (sandevistan.sk), after the Edgerunners spine implant.

  Spine   item elytro:sandevistan_spine, worn as an ItemDisplay riding the player. A gunmetal
          column of eight vertebra plates with heat-sink fins, a neck housing and a lumbar unit,
          a glowing core line and glowing gaps between the plates. custom_model_data string
          "active" (set while the wearer moves) swaps the dim teal glow for bright green.
  Echo    item elytro:sandevistan_echo, the afterimages: a translucent player-shaped hologram
          (a white frame texture, tinted by custom_model_data colour 0). strings[0] picks the
          pose (stand, walk_a, walk_b, run_a, run_b, jump, sneak), strings[1] the fade step
          "0".."3" (0 = strongest). Shown full bright on an ItemDisplay.

Both models share one frame ("body space"): 1 model unit = 1 pixel of the vanilla player model,
the front of the body is +z, the player's right is -x, the feet are at y -8 and the model centre
(8, 8, 8) is 15 px above the feet. The script places it with scale 0.9375 (vanilla's player scale).
The spine is modelled on the standing body (its back is z 6, a chestplate's back z 5); the script
tilts the whole display for crouching, swimming and gliding.

Writes into ./assets/elytro (this folder). Usage (needs Pillow): python sandevistan_build.py [--preview DIR]
"""
import json
import math
import os
import sys

from PIL import Image, ImageDraw

HERE = os.path.dirname(os.path.abspath(__file__))
A = os.path.join(HERE, 'assets', 'elytro')

# ------------------------------------------------------------------ spine palette
PAL = {
    'dark': (30, 32, 38), 'gun': (58, 62, 72), 'steel': (98, 104, 118), 'edge': (150, 158, 172),
    'shine': (196, 204, 216), 'amber': (255, 168, 46), 'pink': (255, 64, 190),
}
GLOW = {'idle': ((40, 196, 170), (22, 120, 108)), 'active': ((120, 255, 150), (60, 255, 210))}
NAMES = list(PAL) + ['glow', 'glow2']
FACES = ('north', 'south', 'east', 'west', 'up', 'down')


def spine_texture(mode):
    im = Image.new('RGBA', (16, 16), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    cols = dict(PAL)
    cols['glow'], cols['glow2'] = GLOW[mode]
    for i, n in enumerate(NAMES):
        x, y = (i % 4) * 4, (i // 4) * 4
        d.rectangle([x, y, x + 3, y + 3], fill=cols[n] + (255,))
    return im


def uv_of(c):
    if c not in NAMES:
        return [0, 0, 16, 16]   # echo frame (and the preview's stand-in body)
    i = NAMES.index(c)
    u, v = (i % 4) * 4, (i // 4) * 4
    return [u + 1, v + 1, u + 3, v + 3]


def box(frm, to, col, rot=None, light=0, faces=None):
    """col: one palette name, or a dict face -> name ('default' for the rest)."""
    f = {}
    for k in FACES:
        c = col if isinstance(col, str) else col.get(k, col.get('default'))
        if c is None or (faces and k not in faces):
            continue
        f[k] = {'uv': uv_of(c), 'texture': '#t'}
    e = {'from': [round(min(a, b), 3) for a, b in zip(frm, to)],
         'to': [round(max(a, b), 3) for a, b in zip(frm, to)], 'faces': f}
    if rot:
        axis, angle, origin = rot
        e['rotation'] = {'axis': axis, 'angle': angle, 'origin': [round(v, 3) for v in origin]}
    if light:
        e['light_emission'] = light
    e['_col'] = col
    return e


# ------------------------------------------------------------------ the spine
# On the standing body: back of the chestplate at z 5, outward is -z; the neck is y 16, the
# waist y 4; the spine runs down x 8.
def spine(mode):
    L = 15 if mode == 'active' else 7
    E = []
    M = {'default': 'gun', 'north': 'steel', 'up': 'edge', 'down': 'dark'}
    # base rail on the chestplate, and the raised column on it
    E.append(box([6.7, 3.6, 4.6], [9.3, 16.4, 5.3], {'default': 'dark', 'north': 'gun'}))
    E.append(box([7.25, 3.9, 3.9], [8.75, 16.6, 4.6], {'default': 'gun', 'north': 'dark'}))
    # glowing core line down the middle of the column
    E.append(box([7.7, 4.2, 3.7], [8.3, 16.3, 3.9], 'glow', light=L, faces=('north', 'east', 'west', 'up', 'down')))
    # vertebrae, widest at the shoulders, each with a glow gap under it and a fin either side
    n = 8
    for i in range(n):
        t = i / (n - 1)
        yc = 15.2 - t * 9.6
        w = 6.0 - t * 2.4
        E.append(box([8 - w / 2, yc - 0.5, 3.35], [8 + w / 2, yc + 0.5, 4.75], M))
        E.append(box([8 - w / 2 + 0.6, yc + 0.5, 3.5], [8 + w / 2 - 0.6, yc + 0.75, 4.6], {'default': 'shine'}))
        E.append(box([7.7, yc - 0.3, 3.2], [8.3, yc + 0.3, 3.35], 'glow', light=L, faces=('north', 'east', 'west', 'up', 'down')))
        if i < n - 1:
            E.append(box([8 - w / 2 + 0.7, yc - 0.85, 3.75], [8 + w / 2 - 0.7, yc - 0.5, 4.6], 'glow2', light=L,
                         faces=('north', 'east', 'west', 'down')))
        fin = 1.5 - t * 0.5
        F = {'default': 'steel', 'up': 'edge', 'down': 'dark'}
        E.append(box([8 - w / 2 - fin, yc - 0.18, 3.85], [8 - w / 2 + 0.2, yc + 0.18, 4.95], F,
                     ('z', -22.5, [8 - w / 2, yc, 4.4])))
        E.append(box([8 + w / 2 - 0.2, yc - 0.18, 3.85], [8 + w / 2 + fin, yc + 0.18, 4.95], F,
                     ('z', 22.5, [8 + w / 2, yc, 4.4])))
    # neck housing with two ports leaning into the base of the skull
    E.append(box([6.1, 15.9, 3.1], [9.9, 17.0, 5.3], {'default': 'gun', 'north': 'steel', 'up': 'edge'}))
    E.append(box([6.6, 16.2, 2.95], [9.4, 16.7, 3.1], 'glow', light=L, faces=('north',)))
    for x0 in (6.4, 8.7):
        E.append(box([x0, 16.6, 4.2], [x0 + 0.9, 18.2, 5.1], {'default': 'dark', 'up': 'steel'},
                     ('x', -22.5, [x0 + 0.45, 16.6, 4.6])))
    # lumbar unit: a housing with vents and two indicator lights
    E.append(box([5.9, 2.6, 3.0], [10.1, 4.4, 5.3], {'default': 'gun', 'north': 'steel', 'up': 'edge', 'down': 'dark'}))
    for k in range(3):
        y = 2.9 + k * 0.5
        E.append(box([6.6, y, 2.9], [9.4, y + 0.22, 3.0], 'dark', faces=('north',)))
    E.append(box([6.2, 3.85, 2.85], [6.8, 4.25, 3.0], 'amber', light=15, faces=('north',)))
    E.append(box([9.2, 3.85, 2.85], [9.8, 4.25, 3.0], 'pink', light=15, faces=('north',)))
    return E


# ------------------------------------------------------------------ the echo (afterimage)
# Built from the vanilla PlayerModel (wide arms), in its own pixel space (y down, front -z),
# then moved into body space: m = (8 + x, 16 - y - drop, 8 - z). A rotation about x keeps its
# angle under that change; a negative xRot swings a limb forward.
PARTS = {
    'head': ((0, 0, 0), (-4, -8, -4), (4, 0, 4)),
    'body': ((0, 0, 0), (-4, 0, -2), (4, 12, 2)),
    'rarm': ((-5, 2, 0), (-3, -2, -2), (1, 10, 2)),
    'larm': ((5, 2, 0), (-1, -2, -2), (3, 10, 2)),
    'rleg': ((-1.9, 12, 0), (-2, 0, -2), (2, 12, 2)),
    'lleg': ((1.9, 12, 0), (-2, 0, -2), (2, 12, 2)),
}
CROUCH_DROP = 2.0 * 16 / 15   # vanilla lowers a crouching player 2/16 block, before its 0.9375 scale

# pose -> part -> (xRot degrees, pivot override)
POSES = {
    'stand': {'rarm': 4, 'larm': -4},
    'walk_a': {'rarm': -30, 'larm': 30, 'rleg': 32, 'lleg': -32},
    'walk_b': {'rarm': 30, 'larm': -30, 'rleg': -32, 'lleg': 32},
    'run_a': {'rarm': -45, 'larm': 45, 'rleg': 45, 'lleg': -45, 'head': -8},
    'run_b': {'rarm': 45, 'larm': -45, 'rleg': -45, 'lleg': 45, 'head': -8},
    'jump': {'rarm': -40, 'larm': 22.5, 'rleg': -40, 'lleg': 15, 'head': -8},
    'sneak': {'body': 28.6, 'rarm': 22.9, 'larm': 22.9, 'head': 0,
              '_pivot': {'head': (0, 4.2, 0), 'body': (0, 3.2, 0), 'rarm': (-5, 5.2, 0), 'larm': (5, 5.2, 0),
                         'rleg': (-1.9, 12.2, 4), 'lleg': (1.9, 12.2, 4)}},
}


def echo(pose):
    P = POSES[pose]
    drop = CROUCH_DROP if pose == 'sneak' else 0
    piv_over = P.get('_pivot', {})
    E = []
    for name, (piv, lo, hi) in PARTS.items():
        piv = piv_over.get(name, piv)
        ang = P.get(name, 0)

        def m(p):
            return [8 + p[0], 16 - p[1] - drop, 8 - p[2]]
        a = m([piv[0] + lo[0], piv[1] + lo[1], piv[2] + lo[2]])
        b = m([piv[0] + hi[0], piv[1] + hi[1], piv[2] + hi[2]])
        if abs(ang) > 45:
            raise ValueError('rotation over 45 degrees: %s %s' % (pose, name))
        rot = ('x', round(ang, 2), m(piv)) if ang else None
        e = box(a, b, 'echo', rot)
        for f in e['faces'].values():
            f['uv'] = [0, 0, 16, 16]
            f['tintindex'] = 0
        E.append(e)
    return E


def echo_texture(level):
    """A white hologram frame: bright rim, softer fill with scanlines. level 0 strongest."""
    rim, fill = ((235, 150), (190, 105), (140, 66), (88, 30))[level]
    im = Image.new('RGBA', (16, 16))
    for y in range(16):
        for x in range(16):
            edge = x in (0, 15) or y in (0, 15)
            a = rim if edge else (fill if y % 3 else int(fill * 0.55))
            im.putpixel((x, y), (255, 255, 255, a))
    return im


# ------------------------------------------------------------------ json
def check(E):
    for e in E:
        for v in e['from'] + e['to']:
            assert -16 <= v <= 32, e
        r = e.get('rotation')
        if r:
            assert -45 <= r['angle'] <= 45, e


def clean(E):
    return [{k: v for k, v in e.items() if k != '_col'} for e in E]


SPINE_DISPLAY = {
    'gui': {'rotation': [8, 155, 0], 'translation': [0, -1.5, 0], 'scale': [1.05, 1.05, 1.05]},
    'ground': {'rotation': [0, 0, 0], 'translation': [0, 2, 0], 'scale': [0.5, 0.5, 0.5]},
    'fixed': {'rotation': [0, 180, 0], 'translation': [0, -1, 0], 'scale': [1, 1, 1]},
    'thirdperson_righthand': {'rotation': [0, 180, 0], 'translation': [0, 0, 2], 'scale': [0.55, 0.55, 0.55]},
    'thirdperson_lefthand': {'rotation': [0, 180, 0], 'translation': [0, 0, 2], 'scale': [0.55, 0.55, 0.55]},
    'firstperson_righthand': {'rotation': [0, 200, 0], 'translation': [1, 1, 0], 'scale': [0.5, 0.5, 0.5]},
    'firstperson_lefthand': {'rotation': [0, 160, 0], 'translation': [1, 1, 0], 'scale': [0.5, 0.5, 0.5]},
}


def write(rel, data):
    path = os.path.join(A, rel)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    if isinstance(data, Image.Image):
        data.save(path)
    else:
        with open(path, 'w', encoding='utf-8', newline='\n') as f:
            json.dump(data, f, indent=1)


def leaf(model, tint=False):
    m = {'type': 'minecraft:model', 'model': model}
    if tint:
        m['tints'] = [{'type': 'minecraft:custom_model_data', 'index': 0, 'default': 0xFFFFFF}]
    return m


# ------------------------------------------------------------------ preview (software render)
def rot3(p, axis, ang, o):
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


def quads(E, colour, alpha=255, glow_cols=None):
    out = []
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
        for f in e['faces']:
            pts = corners[f]
            if 'rotation' in e:
                r = e['rotation']
                pts = [rot3(p, r['axis'], r['angle'], r['origin']) for p in pts]
            c = e['_col'] if isinstance(e['_col'], str) else e['_col'].get(f, e['_col'].get('default'))
            out.append((pts, f, colour(c), alpha, bool(e.get('light_emission'))))
    return out


def render(Q, path, yaw, pitch=10, size=420, span=44, centre=(8, 8, 8)):
    shade = {'north': 0.8, 'south': 0.8, 'east': 0.6, 'west': 0.6, 'up': 1.0, 'down': 0.5}

    def view(p):
        x, y, z = p[0] - centre[0], p[1] - centre[1], p[2] - centre[2]
        a = math.radians(yaw)
        x, z = x * math.cos(a) + z * math.sin(a), -x * math.sin(a) + z * math.cos(a)
        b = math.radians(pitch)
        y, z = y * math.cos(b) - z * math.sin(b), y * math.sin(b) + z * math.cos(b)
        k = size / span
        return (size / 2 - x * k, size / 2 - y * k, z)   # camera on -z looking toward +z
    im = Image.new('RGBA', (size, size), (64, 70, 80, 255))
    items = []
    for pts, f, rgb, alpha, lit in Q:
        vp = [view(p) for p in pts]
        k = 1.15 if lit else shade[f]
        items.append((sum(p[2] for p in vp) / 4, [(p[0], p[1]) for p in vp],
                      tuple(min(255, int(v * k)) for v in rgb), alpha))
    for _, pts, c, a in sorted(items, key=lambda q: -q[0]):
        layer = Image.new('RGBA', im.size, (0, 0, 0, 0))
        ImageDraw.Draw(layer).polygon(pts, fill=c + (a,), outline=tuple(max(0, v - 30) for v in c) + (min(255, a + 40),))
        im.alpha_composite(layer)
    im.save(path)


def preview(out):
    body = []
    for name, (piv, lo, hi) in PARTS.items():
        a = [8 + piv[0] + lo[0], 16 - piv[1] - lo[1], 8 - piv[2] - lo[2]]
        b = [8 + piv[0] + hi[0], 16 - piv[1] - hi[1], 8 - piv[2] - hi[2]]
        body.append(box(a, b, 'skin'))
    body.append(box([3, 3, 5], [13, 17, 11], 'armor'))     # the chestplate's body layer
    cols = dict(PAL)
    cols.update(skin=(176, 132, 104), armor=(150, 150, 160))
    for mode in GLOW:
        cols['glow'], cols['glow2'] = GLOW[mode]
        S = spine(mode)
        Q = quads(body, lambda c: cols[c]) + quads(S, lambda c: cols[c])
        for tag, yaw in (('back', 0), ('three', 35), ('side', 90)):
            render(Q, os.path.join(out, 'spine_%s_%s.png' % (mode, tag)), yaw)
        render(quads(S, lambda c: cols[c]), os.path.join(out, 'spine_%s_close.png' % mode), 25, 8, span=18,
               centre=(8, 10, 4))
    tints = [(57, 255, 136), (0, 236, 255), (255, 60, 200), (255, 226, 60)]
    for i, pose in enumerate(POSES):
        E = echo(pose)
        Q = quads(E, lambda c: tints[i % 4], alpha=150)
        render(Q, os.path.join(out, 'echo_%s_side.png' % pose), 90)
        render(Q, os.path.join(out, 'echo_%s_front.png' % pose), 150)


def build(preview_dir=None):
    for mode in GLOW:
        write('textures/item/sandevistan_%s.png' % mode, spine_texture(mode))
        E = spine(mode)
        check(E)
        write('models/item/sandevistan/spine_%s.json' % mode, {
            'textures': {'t': 'elytro:item/sandevistan_%s' % mode, 'particle': 'elytro:item/sandevistan_%s' % mode},
            'elements': clean(E), 'display': SPINE_DISPLAY})
    write('items/sandevistan_spine.json', {'model': {
        'type': 'minecraft:select', 'property': 'minecraft:custom_model_data', 'index': 0,
        'cases': [{'when': 'active', 'model': leaf('elytro:item/sandevistan/spine_active')}],
        'fallback': leaf('elytro:item/sandevistan/spine_idle')}})
    for lv in range(4):
        write('textures/item/sandevistan_echo_%d.png' % lv, echo_texture(lv))
    pose_cases = []
    for pose in POSES:
        E = echo(pose)
        check(E)
        write('models/item/sandevistan/echo_%s.json' % pose, {
            'textures': {'t': 'elytro:item/sandevistan_echo_0', 'particle': 'elytro:item/sandevistan_echo_0'},
            'elements': clean(E)})
        fades = []
        for lv in range(1, 4):
            write('models/item/sandevistan/echo_%s_%d.json' % (pose, lv), {
                'parent': 'elytro:item/sandevistan/echo_%s' % pose,
                'textures': {'t': 'elytro:item/sandevistan_echo_%d' % lv, 'particle': 'elytro:item/sandevistan_echo_%d' % lv}})
            fades.append({'when': str(lv), 'model': leaf('elytro:item/sandevistan/echo_%s_%d' % (pose, lv), True)})
        sel = {'type': 'minecraft:select', 'property': 'minecraft:custom_model_data', 'index': 1,
               'cases': fades, 'fallback': leaf('elytro:item/sandevistan/echo_%s' % pose, True)}
        if pose == 'stand':
            stand_sel = sel
        else:
            pose_cases.append({'when': pose, 'model': sel})
    write('items/sandevistan_echo.json', {'model': {
        'type': 'minecraft:select', 'property': 'minecraft:custom_model_data', 'index': 0,
        'cases': pose_cases, 'fallback': stand_sel}})
    if preview_dir:
        preview(preview_dir)
    print('Sandevistan: spine %d elements, echo %d poses x 4 fades' % (len(spine('idle')), len(POSES)))


if __name__ == '__main__':
    out = None
    if '--preview' in sys.argv:
        out = sys.argv[sys.argv.index('--preview') + 1]
        os.makedirs(out, exist_ok=True)
    build(out)
