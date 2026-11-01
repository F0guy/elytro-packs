"""Sandevistan - a cosmetic chestplate skin (sandevistan.sk), after the Edgerunners spine implant.

  Worn    the spine is painted onto the chestplate: equipment assets elytro:sandevistan_<material>
          draw the chestplate's own vanilla layer(s) and then an 8x HD overlay
          (textures/entity/equipment/humanoid/sandevistan_spine.png) on the back: a gunmetal
          column of eight vertebra plates with heat-sink fins, a neck housing, a lumbar unit and a
          glowing core. Because the client draws it as armour, it is always exactly on the back
          and in the wearer's pose (turning, crouching, swimming, gliding, riding).
  Voucher item elytro:sandevistan_spine, a 3D model of the same implant (the voucher icon).
  Echo    item elytro:sandevistan_echo, the afterimages: one translucent hologram box per body
          part (head, body, arms wide/slim, leg), tinted by custom_model_data colour 0, with
          strings[0] = part and strings[1] = fade "0".."3". The script poses six of them.

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


def leaf(model):
    return {'type': 'minecraft:model', 'model': model}


# ------------------------------------------------------------------ the painted spine (worn)
# The armour body box's back face is (32..40, 20..32) on the 64x32 layout; at 8x that is a
# 64x96 patch at (256, 160). Armour renders cutout, so every painted pixel is opaque and the rest
# stays clear for the chestplate underneath. Seen from behind, x 0 of the patch is the left edge.
X = 8
BACK = (32 * X, 20 * X)
OUTLINE = (14, 15, 19)
OVER = dict(PAL, glow=(70, 255, 190), glow_hi=(200, 255, 230), glow_dk=(20, 150, 120))


def spine_overlay():
    im = Image.new('RGBA', (64 * X, 32 * X), (0, 0, 0, 0))
    patch = Image.new('RGBA', (64, 96), (0, 0, 0, 0))
    d = ImageDraw.Draw(patch)
    C = {k: v + (255,) for k, v in OVER.items()}
    O = OUTLINE + (255,)

    def rect(x0, y0, x1, y1, c, outline=False):
        if outline:
            d.rectangle([x0 - 1, y0 - 1, x1 + 1, y1 + 1], fill=O)
        d.rectangle([x0, y0, x1, y1], fill=c)

    def bevel(x0, y0, x1, y1, base='gun', hi='edge', lo='dark'):
        rect(x0, y0, x1, y1, C[base], outline=True)
        d.line([x0, y0, x1, y0], fill=C[hi])
        d.line([x0, y1, x1, y1], fill=C[lo])
        d.line([x0, y0, x0, y1], fill=C[hi])
        d.line([x1, y0, x1, y1], fill=C[lo])

    cx = 32
    # the column and its glowing core, under everything
    bevel(cx - 6, 6, cx + 5, 88, 'dark', 'gun', 'dark')
    rect(cx - 2, 8, cx + 1, 86, C['glow_dk'])
    rect(cx - 1, 8, cx, 86, C['glow'])
    # neck housing with a glowing slit
    bevel(cx - 15, 1, cx + 14, 8, 'gun', 'shine', 'dark')
    rect(cx - 11, 4, cx + 10, 5, C['glow'])
    d.line([cx - 11, 4, cx + 10, 4], fill=C['glow_hi'])
    n = 8
    for i in range(n):
        t = i / (n - 1)
        y = int(round(12 + t * 66))
        w = int(round(22 - t * 8))
        # fins: thin blades sloping down and out from the plate ends
        fin = int(round(9 - t * 3))
        for side in (-1, 1):
            x_in = cx + side * w
            tip = min(63, max(0, x_in + side * fin))
            pts = [(x_in, y), (tip, y + 3), (tip, y + 6), (x_in, y + 4)]
            d.polygon([(pts[0][0], y - 1), (tip, y + 2), (tip, y + 7), (x_in, y + 5)], fill=O)
            d.polygon(pts, fill=C['steel'])
            d.line([pts[0], pts[1]], fill=C['shine'])
            d.line([pts[3], pts[2]], fill=C['gun'])
        # the plate
        bevel(cx - w, y, cx + w - 1, y + 4, 'gun', 'shine', 'dark')
        d.line([cx - w + 2, y + 1, cx + w - 3, y + 1], fill=C['steel'])
        rect(cx - 2, y + 1, cx + 1, y + 3, C['glow'])
        d.point([(cx - 1, y + 1), (cx, y + 1)], fill=C['glow_hi'])
        # glowing gap under the plate
        if i < n - 1:
            g = w - 4
            rect(cx - g, y + 6, cx + g - 1, y + 7, C['glow_dk'])
            d.line([cx - g + 1, y + 6, cx + g - 2, y + 6], fill=C['glow'])
    # lumbar unit: vents and two indicator lights
    bevel(cx - 16, 86, cx + 15, 94, 'gun', 'shine', 'dark')
    for k in range(3):
        d.line([cx - 10, 88 + k * 2, cx + 9, 88 + k * 2], fill=C['dark'])
    rect(cx - 14, 88, cx - 12, 90, C['amber'])
    rect(cx + 11, 88, cx + 13, 90, C['pink'])
    im.alpha_composite(patch, BACK)
    return im


MATERIALS = {
    'leather': [{'texture': 'minecraft:leather', 'dyeable': {'color_when_undyed': -6265536}},
                {'texture': 'minecraft:leather_overlay'}],
    'chainmail': [{'texture': 'minecraft:chainmail'}],
    'iron': [{'texture': 'minecraft:iron'}],
    'gold': [{'texture': 'minecraft:gold'}],
    'diamond': [{'texture': 'minecraft:diamond'}],
    'netherite': [{'texture': 'minecraft:netherite'}],
    'copper': [{'texture': 'minecraft:copper'}],
}


# ------------------------------------------------------------------ the afterimages
# Each echo is six ItemDisplays, one per body part, posed by the script with vanilla's own
# player-model maths. A part model is the vanilla box in its part-local pixel space, shifted by
# +8 so the part's pivot sits at the model centre: the script's display transform is then just
# the renderer's matrix for that part (see sdvPart in sandevistan.sk).
# custom_model_data: strings[0] = part, strings[1] = fade "0".."3", colours[0] = tint.
PARTS = {
    'head': ((-4, -8, -4), (4, 0, 4)),
    'body': ((-4, 0, -2), (4, 12, 2)),
    'arm_r': ((-3, -2, -2), (1, 10, 2)),
    'arm_l': ((-1, -2, -2), (3, 10, 2)),
    'arm_r_slim': ((-2, -2, -2), (1, 10, 2)),
    'arm_l_slim': ((-1, -2, -2), (2, 10, 2)),
    'leg': ((-2, 0, -2), (2, 12, 2)),
}
FADES = ((240, 150), (200, 110), (150, 70), (95, 34))   # (rim, fill) alpha per fade step


def echo_texture(level, frames=8):
    """A white hologram frame (bright rim, scanlined fill) with a bright band sweeping down it;
    animated (8 frames, see the .mcmeta)."""
    rim, fill = FADES[level]
    im = Image.new('RGBA', (16, 16 * frames))
    for f in range(frames):
        band = f * 2
        for y in range(16):
            for x in range(16):
                if x in (0, 15) or y in (0, 15):
                    a = rim
                else:
                    a = fill if y % 3 else int(fill * 0.6)
                    if (y - band) % 16 in (0, 1):
                        a = min(255, int(a * 1.7) + 20)
                im.putpixel((x, f * 16 + y), (255, 255, 255, a))
    return im


def echo_part(name):
    lo, hi = PARTS[name]
    e = box([v + 8 for v in lo], [v + 8 for v in hi], 'echo')
    for f in e['faces'].values():
        f['uv'] = [0, 0, 16, 16]
        f['tintindex'] = 0
    return [e]


def build_echo():
    for lv in range(len(FADES)):
        write('textures/item/sandevistan_echo_%d.png' % lv, echo_texture(lv))
        path = os.path.join(A, 'textures/item/sandevistan_echo_%d.png.mcmeta' % lv)
        with open(path, 'w', encoding='utf-8', newline='\n') as f:
            json.dump({'animation': {'frametime': 2, 'interpolate': False}}, f)
    cases = []
    for part in PARTS:
        E = echo_part(part)
        check(E)
        write('models/item/sandevistan/echo_%s.json' % part, {
            'textures': {'t': 'elytro:item/sandevistan_echo_0', 'particle': 'elytro:item/sandevistan_echo_0'},
            'elements': clean(E)})
        fades = []
        for lv in range(1, len(FADES)):
            write('models/item/sandevistan/echo_%s_%d.json' % (part, lv), {
                'parent': 'elytro:item/sandevistan/echo_%s' % part,
                'textures': {'t': 'elytro:item/sandevistan_echo_%d' % lv, 'particle': 'elytro:item/sandevistan_echo_%d' % lv}})
            fades.append({'when': str(lv), 'model': tinted('elytro:item/sandevistan/echo_%s_%d' % (part, lv))})
        cases.append({'when': part, 'model': {
            'type': 'minecraft:select', 'property': 'minecraft:custom_model_data', 'index': 1,
            'cases': fades, 'fallback': tinted('elytro:item/sandevistan/echo_%s' % part)}})
    write('items/sandevistan_echo.json', {'model': {
        'type': 'minecraft:select', 'property': 'minecraft:custom_model_data', 'index': 0,
        'cases': cases, 'fallback': {'type': 'minecraft:empty'}}})


def tinted(model):
    return {'type': 'minecraft:model', 'model': model,
            'tints': [{'type': 'minecraft:custom_model_data', 'index': 0, 'default': 0xFFFFFF}]}


def preview(out):
    tex = spine_overlay()
    back = tex.crop((BACK[0], BACK[1], BACK[0] + 64, BACK[1] + 96))
    bg = Image.new('RGBA', (64, 96), (150, 152, 160, 255))
    iron = os.environ.get('IRON_PNG')   # vanilla humanoid/iron.png, for a truer preview
    if iron:
        bg = Image.open(iron).convert('RGBA').crop((32, 20, 40, 32)).resize((64, 96), Image.NEAREST)
    bg.alpha_composite(back)
    bg.resize((256, 384), Image.NEAREST).save(os.path.join(out, 'worn_spine_back.png'))


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
    write('textures/entity/equipment/humanoid/sandevistan_spine.png', spine_overlay())
    for mat, layers in MATERIALS.items():
        write('equipment/sandevistan_%s.json' % mat, {'layers': {
            'humanoid': layers + [{'texture': 'elytro:sandevistan_spine'}]}})
    build_echo()
    if preview_dir:
        preview(preview_dir)
    print('Sandevistan: voucher model %d elements; worn overlay on %d materials; echo %d parts x %d fades'
          % (len(spine('idle')), len(MATERIALS), len(PARTS), len(FADES)))


if __name__ == '__main__':
    out = None
    if '--preview' in sys.argv:
        out = sys.argv[sys.argv.index('--preview') + 1]
        os.makedirs(out, exist_ok=True)
    build(out)
