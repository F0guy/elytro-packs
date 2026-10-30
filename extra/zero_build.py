"""Zero - Lelouch's outfit for the Geass (owners' toy, /zero in geass.sk).

  Mask    a 3D item model worn on the head (equippable HEAD with no equipment asset, so the item
          model itself is drawn there): black shell, a smooth violet visor, a fan of crest spikes
          and the tall purple/red collar behind the head. A shutter over the left eye slides up
          to show the glowing Geass eye: frames chosen by custom_model_data string "o1", "o2",
          "open" (anything else = closed), stepped by the script.
  Suit    equipment asset elytra:zero: humanoid (coat, capelet, cravat, sleeves, boots),
          humanoid_leggings (trousers and coat tails) and wings - the cloak. A chest item whose
          equipment asset has a wings layer draws the elytra model, which hangs from the shoulders
          like a split cape, sways as you move and spreads when you crouch; no glider component,
          so it never flies.

Writes into ./assets/elytro (this folder). Usage (needs Pillow): python zero_build.py [--preview DIR]
"""
import json
import math
import os
import sys

from PIL import Image, ImageDraw

HERE = os.path.dirname(os.path.abspath(__file__))
A = os.path.join(HERE, 'assets', 'elytro')
sys.path.insert(0, HERE)
from geass_build import sigil  # noqa: E402

# ------------------------------------------------------------------ palette (mask texture)
PAL = {
    'shell': (23, 18, 31), 'shell_hi': (44, 36, 56), 'shell_lo': (12, 9, 17),
    'visor': (64, 46, 128), 'visor_dk': (37, 26, 82), 'visor_hi': (214, 206, 255),
    'panel': (82, 62, 150), 'panel_dk': (42, 31, 90),
    'gold': (216, 176, 74), 'gold_dk': (150, 118, 40),
    'collar_out': (48, 35, 104), 'collar_in': (142, 28, 51),
}
NAMES = list(PAL)
EYE = 'eye'


def mask_texture():
    """64x64: 4x4 swatches along the top rows, the eye (black slit, red Geass iris) at 48,48."""
    im = Image.new('RGBA', (64, 64), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    for i, n in enumerate(NAMES):
        x, y = (i % 16) * 4, (i // 16) * 4
        d.rectangle([x, y, x + 3, y + 3], fill=PAL[n] + (255,))
    eye = Image.new('RGBA', (16, 16), (8, 4, 8, 255))
    iris = sigil(12, wings=0.9, iris=True)
    eye.alpha_composite(iris, (2, 2))
    im.alpha_composite(eye, (48, 48))
    return im


def uv_of(c):
    if c == EYE:
        return [12, 12, 16, 16]
    i = NAMES.index(c)
    u, v = (i % 16), (i // 16)
    return [u + 0.25, v + 0.25, u + 0.75, v + 0.75]


FACES = ('north', 'south', 'east', 'west', 'up', 'down')


def box(frm, to, col, rot=None, faces=None, light=0):
    """col: one palette name for every face, or a dict face -> name (missing faces use 'default')."""
    f = {}
    for k in FACES:
        c = col if isinstance(col, str) else col.get(k, col.get('default'))
        if c is None:
            continue
        if faces and k not in faces:
            continue
        f[k] = {'uv': uv_of(c), 'texture': '#t'}
    e = {'from': [round(v, 3) for v in frm], 'to': [round(v, 3) for v in to], 'faces': f}
    if rot:
        axis, angle, origin = rot
        e['rotation'] = {'axis': axis, 'angle': angle, 'origin': [round(v, 3) for v in origin]}
    if light:
        e['light_emission'] = light
    e['_col'] = col
    return e


# ------------------------------------------------------------------ the mask
# Model space: the head occupies 1.6..14.4 on every axis (worn items are drawn at 0.625 scale);
# the face is north (-z). The wearer's left eye is toward -x, at about x 4.8, y 7.6.
def mask(open_frac):
    E = []
    S = {'default': 'shell', 'up': 'shell_hi', 'down': 'shell_lo'}
    # shell, stepped in at the top so the dome reads round
    E.append(box([1.1, 1.6, 1.5], [14.9, 13.0, 14.9], S))
    E.append(box([1.7, 13.0, 2.0], [14.3, 14.4, 14.4], S))
    E.append(box([2.9, 14.4, 3.0], [13.1, 15.4, 13.6], S))
    E.append(box([7.2, 15.2, 2.2], [8.8, 15.8, 14.0], {'default': 'shell_hi'}))     # centre ridge
    # visor: an oval of violet bands bulging forward in the middle, narrowing to the chin
    V = {'default': 'visor_dk', 'north': 'visor'}
    for x0, x1, y0, y1, z0 in ((4.4, 11.6, 13.0, 14.3, 1.1), (3.2, 12.8, 11.6, 13.0, 0.8),
                               (2.3, 13.7, 3.6, 11.6, 0.6), (3.2, 12.8, 2.2, 3.6, 0.8),
                               (4.6, 11.4, 1.0, 2.2, 0.9), (6.2, 9.8, -0.3, 1.0, 1.0)):
        E.append(box([x0, y0, z0], [x1, y1, 1.6], V))
    E.append(box([4.6, 2.6, 0.25], [11.4, 12.4, 0.7], V))                         # forward bulge
    E.append(box([1.4, 3.4, 1.2], [2.6, 11.6, 3.0], {'default': 'visor_dk'}, ('y', -30, [2.3, 7.5, 1.6])))
    E.append(box([13.4, 3.4, 1.2], [14.6, 11.6, 3.0], {'default': 'visor_dk'}, ('y', 30, [13.7, 7.5, 1.6])))
    # the light catching the visor
    E.append(box([9.6, 3.4, 0.1], [10.1, 11.6, 0.25], 'visor_hi', ('z', 22.5, [9.8, 7.5, 0.2]), faces=('north',)))
    E.append(box([5.6, 11.1, 0.55], [7.8, 11.5, 0.7], 'visor_hi', ('z', -22.5, [6.7, 11.3, 0.6]), faces=('north',)))
    # crest: a crown of blades, the middle one tallest, two more swept back behind it
    B = {'default': 'shell', 'up': 'shell_hi', 'north': 'shell_hi'}
    for angle, h, dx in ((0, 9.5, 0.0), (22.5, 8.0, -2.0), (-22.5, 8.0, 2.0), (45, 6.2, -3.8), (-45, 6.2, 3.8)):
        x = 8 + dx
        base = 14.0
        r = ('z', angle, [x, base, 8.0]) if angle else None
        E.append(box([x - 1.0, base, 5.6], [x + 1.0, base + h, 10.4], B, r))
        E.append(box([x - 0.5, base + h, 6.6], [x + 0.5, base + h + 2.0, 9.4], {'default': 'shell_hi'}, r))
    for dx in (-1.6, 1.6):
        r = ('x', 22.5, [8 + dx, 14.0, 11.0])
        E.append(box([8 + dx - 0.8, 14.0, 10.0], [8 + dx + 0.8, 21.0, 12.4], B, r))
    # tall collar behind the head: purple outside, red inside, gold along the top
    C = {'default': 'collar_out', 'north': 'collar_in', 'up': 'gold'}
    E.append(box([0.4, -1.5, 15.0], [8.0, 11.5, 16.0], C, ('y', -22.5, [8.0, 5.0, 15.5])))
    E.append(box([8.0, -1.5, 15.0], [15.6, 11.5, 16.0], C, ('y', 22.5, [8.0, 5.0, 15.5])))
    E.append(box([0.6, 11.5, 15.1], [8.0, 11.9, 15.9], {'default': 'gold'}, ('y', -22.5, [8.0, 5.0, 15.5])))
    E.append(box([8.0, 11.5, 15.1], [15.4, 11.9, 15.9], {'default': 'gold'}, ('y', 22.5, [8.0, 5.0, 15.5])))
    # the left eye: the Geass under a shutter that slides up into the brow
    E.append(box([3.2, 6.8, -0.05], [6.4, 8.4, 0.25], {'default': 'visor_dk', 'north': EYE}, light=15 if open_frac > 0 else 0))
    lift = 2.6 * open_frac
    P = {'default': 'panel_dk', 'north': 'panel'}
    E.append(box([2.9, 6.5 + lift, -0.35], [6.7, 8.7 + lift, -0.05], P))
    return E


def check(E):
    for e in E:
        for v in e['from'] + e['to']:
            assert -16 <= v <= 32, e
        r = e.get('rotation')
        if r:
            assert -45 <= r['angle'] <= 45, e


def model_json(E):
    els = [{k: v for k, v in e.items() if k != '_col'} for e in E]
    return {
        'textures': {'t': 'elytro:item/zero_mask', 'particle': 'elytro:item/zero_mask'},
        'elements': els,
        'display': {
            'head': {'rotation': [0, 0, 0], 'translation': [0, 0, 0], 'scale': [1, 1, 1]},
            'gui': {'rotation': [12, 160, 0], 'translation': [0, -2.2, 0], 'scale': [0.46, 0.46, 0.46]},
            'ground': {'rotation': [0, 0, 0], 'translation': [0, 2, 0], 'scale': [0.3, 0.3, 0.3]},
            'fixed': {'rotation': [0, 180, 0], 'translation': [0, -1, 0], 'scale': [0.5, 0.5, 0.5]},
            'thirdperson_righthand': {'rotation': [0, 180, 0], 'translation': [0, 1, 1], 'scale': [0.35, 0.35, 0.35]},
            'thirdperson_lefthand': {'rotation': [0, 180, 0], 'translation': [0, 1, 1], 'scale': [0.35, 0.35, 0.35]},
            'firstperson_righthand': {'rotation': [0, 200, 0], 'translation': [1, 2, 0], 'scale': [0.3, 0.3, 0.3]},
            'firstperson_lefthand': {'rotation': [0, 160, 0], 'translation': [1, 2, 0], 'scale': [0.3, 0.3, 0.3]},
        },
    }


# ------------------------------------------------------------------ suit textures (8x HD)
X = 8
PURPLE = (43, 33, 96)
PURPLE_DK = (29, 22, 66)
VIOLET = (104, 79, 200)
BLACK = (20, 16, 25)
GOLD = (216, 176, 74)
GOLD_DK = (150, 118, 40)
WHITE = (232, 228, 245)
GEM = (47, 211, 138)
RED = (140, 24, 48)
RED_DK = (98, 14, 32)


class Paint:
    def __init__(self, w=64, h=32):
        self.im = Image.new('RGBA', (w * X, h * X), (0, 0, 0, 0))
        self.d = ImageDraw.Draw(self.im)

    def rect(self, x0, y0, x1, y1, col):
        self.d.rectangle([x0 * X, y0 * X, x1 * X - 1, y1 * X - 1], fill=col + (255,))

    def line(self, pts, col, w=0.5):
        self.d.line([(x * X, y * X) for x, y in pts], fill=col + (255,), width=max(1, int(w * X)))

    def poly(self, pts, col):
        self.d.polygon([(x * X, y * X) for x, y in pts], fill=col + (255,))

    def zigzag(self, x0, x1, y, amp, col, w=0.45, n=4):
        pts = []
        for i in range(n * 2 + 1):
            pts.append((x0 + (x1 - x0) * i / (n * 2), y + (amp if i % 2 else 0)))
        self.line(pts, col, w)

    def shade(self, x0, y0, x1, y1, strength=0.25):
        """Darken toward the bottom so flat cloth reads as falling."""
        px = self.im.load()
        for y in range(int(y0 * X), int(y1 * X)):
            t = (y - y0 * X) / max(1, (y1 - y0) * X)
            k = 1 - strength * t
            for x in range(int(x0 * X), int(x1 * X)):
                r, g, b, a = px[x, y]
                if a:
                    px[x, y] = (int(r * k), int(g * k), int(b * k), a)


def suit():
    """humanoid layer: body + arms (chestplate) and the lower legs (boots)."""
    p = Paint()
    # ---- body: front 20..28, back 32..40, sides 16..20 / 28..32, rows 20..32; top 20..28 x 16..20
    for x0, x1 in ((16, 20), (20, 28), (28, 32), (32, 40)):
        p.rect(x0, 20, x1, 32, PURPLE)
        p.rect(x0, 20, x1, 23.5, BLACK)                    # capelet over the shoulders
        p.zigzag(x0, x1, 23.5, 0.8, GOLD, n=2 if x1 - x0 <= 4 else 3)
    p.rect(20, 16, 28, 20, BLACK)
    p.rect(28, 16, 36, 20, PURPLE_DK)
    # front: cravat, gem, and the gold chevrons down the coat
    p.poly([(22.6, 20), (25.4, 20), (25.0, 22.4), (24, 23.4), (23.0, 22.4)], WHITE)
    p.rect(23.7, 23.3, 24.3, 24.3, GEM)
    p.line([(20.6, 24.6), (24, 29.4), (27.4, 24.6)], GOLD, 0.45)
    p.line([(21.4, 27.0), (24, 31.4), (26.6, 27.0)], GOLD, 0.35)
    p.line([(24, 24.6), (24, 32)], GOLD_DK, 0.3)
    p.rect(20, 31.4, 28, 32, GOLD_DK)
    p.shade(16, 23.5, 40, 32, 0.22)
    # ---- right arm (the left arm mirrors it): 40..56 x 20..32, top 44..48 x 16..20
    for x0 in (40, 44, 48, 52):
        p.rect(x0, 20, x0 + 4, 32, PURPLE)
        p.rect(x0, 20, x0 + 4, 22.5, BLACK)                # capelet over the shoulder
        p.zigzag(x0, x0 + 4, 22.5, 0.6, GOLD, n=1)
        p.rect(x0, 28.2, x0 + 4, 30.6, VIOLET)             # violet cuff, gold-edged
        p.line([(x0, 28.2), (x0 + 4, 28.2)], GOLD, 0.3)
        p.line([(x0, 30.6), (x0 + 4, 30.6)], GOLD, 0.25)
        p.rect(x0, 30.6, x0 + 4, 32, BLACK)                # glove
    p.line([(46, 28.2), (45.2, 26.4), (47.4, 27.4)], GOLD, 0.25)   # cuff points (front)
    p.rect(44, 16, 48, 20, BLACK)
    p.rect(48, 16, 52, 20, BLACK)
    p.shade(40, 22.5, 56, 28, 0.18)
    # ---- boots on the lower legs: 0..16 x 20..32 (rows 26..32), soles 8..12 x 16..20
    for x0 in (0, 4, 8, 12):
        p.rect(x0, 26, x0 + 4, 32, PURPLE_DK)
        p.line([(x0, 26), (x0 + 4, 26)], GOLD, 0.35)
    p.poly([(4, 32), (8, 32), (7.2, 30.4), (6, 29.2), (4.8, 30.4)], GOLD)   # gold toe cap
    p.line([(6, 26), (6, 29.2)], GOLD, 0.3)
    p.rect(8, 16, 12, 20, BLACK)
    return p.im


def legs():
    """humanoid_leggings layer: the lower coat (waist) and trousers with gold stripes."""
    p = Paint()
    for x0, x1 in ((16, 20), (20, 28), (28, 32), (32, 40)):
        p.rect(x0, 27, x1, 32, PURPLE)
        p.line([(x0, 27), (x1, 27)], GOLD, 0.35)
    p.line([(24, 27), (24, 32)], GOLD_DK, 0.3)
    for x0 in (0, 4, 8, 12):
        p.rect(x0, 20, x0 + 4, 32, PURPLE_DK)
    p.rect(4, 20, 8, 25, PURPLE)                           # coat tail over the thigh
    p.line([(4.3, 20), (4.3, 25), (6, 26.4), (7.7, 25), (7.7, 20)], GOLD, 0.35)
    p.line([(0.6, 20), (0.6, 32)], GOLD, 0.3)              # side stripes
    p.line([(11.4, 20), (11.4, 32)], GOLD, 0.3)
    p.rect(4, 16, 8, 20, PURPLE_DK)
    p.shade(0, 20, 16, 32, 0.25)
    return p.im


def cloak():
    """wings layer (the elytra's 64x32 layout): each wing is a 10x20x2 box at u 22, v 0. Both big
    faces are painted - violet outside, red inside - with gold all round the edges."""
    p = Paint()
    p.rect(24, 2, 34, 22, (42, 31, 94))
    p.rect(36, 2, 46, 22, RED)
    for x0 in (24, 36):
        dark = (28, 20, 64) if x0 == 24 else RED_DK
        for k in range(3):                                 # long folds
            fx = x0 + 2 + k * 3
            p.rect(fx, 4, fx + 0.8, 22, dark)
        p.rect(x0, 2, x0 + 10, 3.4, BLACK)                 # under the capelet
        p.zigzag(x0, x0 + 10, 3.4, 0.7, GOLD, n=3)
        p.rect(x0, 21.2, x0 + 10, 22, GOLD)                # hem
        p.rect(x0, 3.4, x0 + 0.5, 22, GOLD)
        p.rect(x0 + 9.5, 3.4, x0 + 10, 22, GOLD)
        p.shade(x0, 3.4, x0 + 10, 21.2, 0.3)
    p.rect(22, 2, 24, 22, GOLD)
    p.rect(34, 2, 36, 22, GOLD)
    p.rect(24, 0, 44, 2, GOLD_DK)
    return p.im


# ------------------------------------------------------------------ preview (software render)
def preview(E, path, yaw, pitch=12, size=320):
    """Painter's-algorithm render of the boxes (rotations applied as Minecraft does), for checking."""
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
        a = math.radians(yaw)
        x, z = x * math.cos(a) + z * math.sin(a), -x * math.sin(a) + z * math.cos(a)
        b = math.radians(pitch)
        y, z = y * math.cos(b) - z * math.sin(b), y * math.sin(b) + z * math.cos(b)
        k = size / 40
        return (size / 2 - x * k, size * 0.62 - y * k, z)   # camera looks toward +z from -z

    quads = []
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
        shade = {'north': 0.8, 'south': 0.8, 'east': 0.6, 'west': 0.6, 'up': 1.0, 'down': 0.5}
        col = e['_col']
        for f in e['faces']:
            pts = corners[f]
            if 'rotation' in e:
                r = e['rotation']
                pts = [rot(p, r['axis'], r['angle'], r['origin']) for p in pts]
            vp = [view(p) for p in pts]
            c = col if isinstance(col, str) else col.get(f, col.get('default'))
            rgb = (220, 40, 70) if c == EYE else PAL[c]
            if c == EYE and e.get('light_emission'):
                k = 1.2
            else:
                k = shade[f]
            quads.append((sum(p[2] for p in vp) / 4, [(p[0], p[1]) for p in vp], tuple(min(255, int(v * k)) for v in rgb)))
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
            json.dump(data, f, indent=1)


FRAMES = (('closed', 0.0), ('o1', 0.33), ('o2', 0.66), ('open', 1.0))


def build(preview_dir=None):
    write('textures/item/zero_mask.png', mask_texture())
    cases = []
    for name, f in FRAMES:
        E = mask(f)
        check(E)
        write('models/item/zero_mask_%s.json' % name, model_json(E))
        if name != 'closed':
            cases.append({'when': name, 'model': {'type': 'minecraft:model', 'model': 'elytro:item/zero_mask_' + name}})
        if preview_dir:
            for tag, yaw in (('front', 0), ('three', 35), ('side', 90), ('back', 180)):
                preview(E, os.path.join(preview_dir, 'zero_%s_%s.png' % (name, tag)), yaw)
    write('items/zero_mask.json', {'model': {
        'type': 'minecraft:select', 'property': 'minecraft:custom_model_data', 'index': 0, 'cases': cases,
        'fallback': {'type': 'minecraft:model', 'model': 'elytro:item/zero_mask_closed'}}})
    write('textures/entity/equipment/humanoid/zero.png', suit())
    write('textures/entity/equipment/humanoid_leggings/zero_legs.png', legs())
    write('textures/entity/equipment/wings/zero_cloak.png', cloak())
    write('equipment/zero.json', {'layers': {
        'humanoid': [{'texture': 'elytro:zero'}],
        'humanoid_leggings': [{'texture': 'elytro:zero_legs'}],
        'wings': [{'texture': 'elytro:zero_cloak'}]}})
    print('Zero: mask %d elements, %d frames; suit, legs, cloak written' % (len(mask(0)), len(FRAMES)))


if __name__ == '__main__':
    out = None
    if '--preview' in sys.argv:
        out = sys.argv[sys.argv.index('--preview') + 1]
        os.makedirs(out, exist_ok=True)
    build(out)
