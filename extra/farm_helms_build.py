"""Farm Armor helms v20 (visors: sprout Y, sprout Y, T, furrow, harvest arch) (elytro:farm_cap_1..5): farming built into the construction.

The theme is in the structure, not glued on: the centre ridge is a plant stem that
splits the dark face and feeds leaf veins engraved across the forehead; the brow is a
crescent sickle blade; the sides carry layered husk plates stepping up and back like
leaves wrapped round an ear; each crest is a crop or tool laid along the crown. The
magic stays small: lit eyes in the recess, and on the top tier a lit seed in the brow
with faint light in the veins.
  1 Sprout     seed husk shell, a shoot breaking from the crown seam, one husk layer
  2 Harvester  straw-gold shell, bronze sickle brow, a wheat ear crest, two husk layers
  3 Thresher   dark oak and bronze, a crest of three bound stalks, neck guard
  4 Reaper     plum iron, steel sickle brow, a scythe blade arcing over the crown
  5 Verdant    deep forest green and aged gold, a great leaf crest, three husk layers,
               a gold seed set in the brow
Same voxel craft as before: hand-placed 8x8 faces, 1 pixel = 2 model units.
Usage: python helm17_build.py <out assets/elytro dir> [sheet preview png]
"""
import json, os, sys
from PIL import Image

OUT = sys.argv[1]
T = 256
UVU = T / 16
tex = Image.new('RGBA', (T, T), (0, 0, 0, 0))
PX = tex.load()
TILE = {}
_slot = [0]


def hexc(s):
    return tuple(int(s[i:i + 2], 16) for i in (1, 3, 5))


def put(name, rows, pal):
    assert len(rows) == 8 and all(len(r) == 8 for r in rows), (name, rows)
    i = _slot[0]; _slot[0] += 1
    x0, y0 = (i % 32) * 8, (i // 32) * 8
    for y, r in enumerate(rows):
        for x, ch in enumerate(r):
            PX[x0 + x, y0 + y] = (hexc(pal[ch]) + (255,)) if ch != '.' else (0, 0, 0, 0)
    TILE[name] = (x0, y0)


# ------------------------------------------------------------- shared grids
# digits 1..5 = shell ramp, k = face recess, e = eye light, v = engraved leaf veins
# the sprout visor: a stem rising from the chin that opens into two leaves at the eyes,
# cut through the faceplate ('.'), rimmed one shade darker; leaf veins on the forehead
FRONT = ["45v44v54",
         "225vv522",
         "..2332..",
         "2..22..2",
         "32....23",
         "332..233",
         "332..232",
         "222..221"]
# Verdant's face: furrows. One open eye line lit along its whole length, with two
# shallower furrows cut below it, narrowing like ploughed rows running away from you.
FURROW = ["45v44v54",
          "445vv544",
          "32222223",
          "2......2",
          "33444433",
          "33111133",
          "33344333",
          "3331133 ".replace(' ', '2')]
# Thresher's face: the classic T, a one-pixel bar across the eyes and a stem to the chin.
TVIS = ["45v44v54",
        "445vv544",
        "32222223",
        "2......2",
        "322..223",
        "332..233",
        "332..232",
        "222..221"]
# Verdant's face: the harvest arch. A lit arch over the eyes whose ends sweep down past
# them, like a sickle moon, with a stem dropping from its crown to the chin.
ARCH = ["45v44v54",
        "445vv544",
        "32....23",
        "3.2..2.3",
        ".22..22.",
        ".32..23.",
        "332..233",
        "222..221"]
SIDE = ["44544443",           # a leaf engraved into each side: midrib running up and back, side veins
        "433333v3",
        "333v3v33",
        "3333v3v3",
        "3v3v3332",
        "33v3v322",
        "2v222222",
        "22222221"]
BACK = ["44544443",
        "33332333",
        "33332333",
        "33332332",
        "33332332",
        "32332322",
        "22232222",
        "22222221"]
TOP = ["45555544",
       "55554444",
       "55444444",
       "54444443",
       "44444443",
       "44444433",
       "44444333",
       "44443333"]
PLATE = ["55555554", "44444443", "44444443", "33333332", "33333332", "33333332", "22222221", "22222221"]
LEAF = ["cccccccc", "bbbcbbbb", "bbbbcbbb", "bbbbbcbb", "abbbbbcb", "aabbbbbb", "aaaaaaaa", "aaaaaaaa"]
BLADE = ["zzzzzzzz", "yyyyyyyy", "yyyyyyyy", "yyyyyyyy", "xxxxxxxx", "xxxxxxxx", "xxxxxxxx", "xxxxxxxx"]
GRAIN = ["hhhhhhhh", "gggggggg", "gggggggg", "gggggggg", "gggggggg", "gggggggg", "gggggggg", "gggggggg"]

# shell ramp, leaf (a b c), blade metal (x y z), grain (g h), recess k, light e
TIERS = {
    1: dict(shell=('#34341E', '#46462A', '#5A5934', '#706E40', '#86844E'), leaf=('#3C5E22', '#527A2C', '#6C9838'),
            blade=('#6E5428', '#8E6E36', '#B8945A'), grain=('#B89A48', '#D6B86A'), k='#121208', e='#A6F07A'),
    2: dict(shell=('#4A3A1C', '#5E4A24', '#76602E', '#8E7638', '#A88E46'), leaf=('#4A5E24', '#5E762E', '#76903A'),
            blade=('#7A5A26', '#A07A36', '#D0A858'), grain=('#C49A3C', '#E6C468'), k='#140E06', e='#FFC25A'),
    3: dict(shell=('#2E2016', '#3C2A1C', '#4C3624', '#5E442E', '#72543A'), leaf=('#40582A', '#546E34', '#6A8840'),
            blade=('#7A4E22', '#A06A2E', '#CC8E44'), grain=('#B88A34', '#D8AC54'), k='#100A06', e='#FF9440'),
    4: dict(shell=('#22182A', '#2E2038', '#3C2A48', '#4C365A', '#5E446E'), leaf=('#3A4A2E', '#4C5E3A', '#627848'),
            blade=('#5E5E6C', '#8A8A9A', '#CACAD6'), grain=('#8A8A9A', '#CACAD6'), k='#0C0812', e='#BE92FF'),
    5: dict(shell=('#142A1C', '#1C3A26', '#264A30', '#305C3A', '#3E7046'), leaf=('#2E5E2A', '#3E7A34', '#56963E'),
            blade=('#7A5C24', '#A68236', '#D6B05A'), grain=('#E0BC5C', '#FFE09A'), k='#08120C', e='#A6F0A0'),
}
for n, t in TIERS.items():
    pal = {str(i + 1): c for i, c in enumerate(t['shell'])}
    pal.update(k=t['k'], e=t['e'], a=t['leaf'][0], b=t['leaf'][1], c=t['leaf'][2],
               x=t['blade'][0], y=t['blade'][1], z=t['blade'][2], g=t['grain'][0], h=t['grain'][1])
    pal['v'] = t['blade'][1] if n == 5 else t['shell'][4]     # the top tier's veins are inlaid gold, not lit
    put('%d_front' % n, {3: TVIS, 4: FURROW, 5: ARCH}.get(n, FRONT), pal)
    put('%d_side' % n, SIDE, pal)
    put('%d_back' % n, BACK, pal)
    put('%d_top' % n, TOP, pal)
    put('%d_bottom' % n, ["11111111"] * 8, pal)
    put('%d_plate' % n, PLATE, pal)
    put('%d_leaf' % n, LEAF, pal)
    put('%d_blade' % n, BLADE, pal)
    put('%d_grain' % n, GRAIN, pal)
    put('%d_eye' % n, ["eeeeeeee"] * 8, pal)
    put('%d_wall' % n, ["11111111", "1k1k1k1k", "kkkkkkkk", "kkkkkkkk", "kkkkkkkk", "kkkkkkkk", "kkkkkkkk", "kkkkkkkk"], pal)
    put('%d_recess' % n, ["kkkkkkkk"] * 8, pal)

os.makedirs(os.path.join(OUT, 'textures', 'item'), exist_ok=True)
tex.save(os.path.join(OUT, 'textures', 'item', 'farm_caps.png'))
if len(sys.argv) > 2:
    im = tex.crop((0, 0, 256, 16))
    bg = Image.new('RGBA', im.size, (60, 60, 70, 255)); bg.alpha_composite(im)
    bg.resize((im.width * 4, im.height * 4), Image.NEAREST).save(sys.argv[2])


# ------------------------------------------------------------- geometry
def uv_px(name, pw, ph, flip=False):
    x, y = TILE[name]
    pw, ph = max(1, min(8, pw)), max(1, min(8, ph))
    r = [round(v / UVU, 4) for v in (x, y, x + pw, y + ph)]
    return [r[2], r[1], r[0], r[3]] if flip else r


def block(a, b, m):
    dx, dy, dz = b[0] - a[0], b[1] - a[1], b[2] - a[2]
    size = {'north': (dx, dy), 'south': (dx, dy), 'east': (dz, dy), 'west': (dz, dy), 'up': (dx, dz), 'down': (dx, dz)}
    e = {'from': list(a), 'to': list(b),
         'faces': {d: {'uv': uv_px(m, round(w / 2 + 0.01), round(h / 2 + 0.01)), 'texture': '#0'} for d, (w, h) in size.items()}}
    return e


def proj(name, dirn, a, b):
    """uv for the part of an 8x8 face tile that a box face covers, so split blocks line up"""
    x, y = TILE[name]
    if dirn == 'north': u0, u1, v0, v1 = (16 - b[0]) / 2, (16 - a[0]) / 2, (16 - b[1]) / 2, (16 - a[1]) / 2
    elif dirn == 'south': u0, u1, v0, v1 = a[0] / 2, b[0] / 2, (16 - b[1]) / 2, (16 - a[1]) / 2
    elif dirn in ('west', 'east'): u0, u1, v0, v1 = a[2] / 2, b[2] / 2, (16 - b[1]) / 2, (16 - a[1]) / 2
    else: u0, u1, v0, v1 = a[0] / 2, b[0] / 2, a[2] / 2, b[2] / 2
    r = [round(v / UVU, 4) for v in (x + u0, y + v0, x + u1, y + v1)]
    return [r[2], r[1], r[0], r[3]] if dirn == 'east' else r


SKIN = {'north': 'front', 'south': 'back', 'west': 'side', 'east': 'side', 'up': 'top', 'down': 'bottom'}


def shell(n, a, b, walls=(), skip=()):
    """a part of the head cube; walls = faces that look into the face recess"""
    fs = {}
    for d, k in SKIN.items():
        if d in skip:
            continue
        if d in walls:
            fs[d] = {'uv': uv_px('%d_wall' % n, 8, 2), 'texture': '#0'}
        else:
            fs[d] = {'uv': proj('%d_%s' % (n, k), d, a, b), 'texture': '#0'}
    return {'from': list(a), 'to': list(b), 'faces': fs}


def head(n):
    """the head: a faceplate one pixel proud of a dark face, the sprout visor cut through it
    (built outward, so the recess never cuts into the wearer's own head)"""
    els = [shell(n, (0, 0, 0), (16, 16, 16), skip=('north',)),
           {'from': [0, 0, 0], 'to': [16, 16, 0], 'faces': {'north': {'uv': uv_px('%d_recess' % n, 8, 8), 'texture': '#0'}}},
           shell(n, (0, 0, -2), (16, 16, 0), skip=('south',))]
    # light deep in the visor: in each leaf (Y), at each end of the T bar, along the furrow
    # eye line, or along the crown of the arch
    eyes = {3: ((2, 4, 8), (12, 14, 8)), 4: ((2, 14, 8),), 5: ((4, 12, 10),)}.get(n, ((2, 4, 8), (12, 14, 8)))
    for (x0, x1, y0) in eyes:
        els.append({'from': [x0, y0, -0.05], 'to': [x1, y0 + 2, -0.05], 'light_emission': 12,
                    'faces': {'north': {'uv': uv_px('%d_eye' % n, 1, 1), 'texture': '#0'}}})
    return els


def stem(n):
    """the centre ridge is a plant stem: it splits the dark face and feeds the leaf veins on the forehead"""
    return [block((7, 0, -1), (9, 12, 0), '%d_leaf' % n)]


def sickle_brow(n, lift=0):
    """the brow is a crescent blade lying over the leaf eyes, its ends curving up like a sickle"""
    m = '%d_blade' % n
    return [block((2, 12 + lift, -4), (14, 13 + lift, -2), m),
            block((0, 12 + lift, -4), (2, 15 + lift, -2), m), block((14, 12 + lift, -4), (16, 15 + lift, -2), m)]


def leaf_brow(n):
    return [block((0, 12, -4), (16, 13, -2), '%d_leaf' % n)]


def husk(n, layers):
    """layered husk plates on both sides, stepping up and back like leaves wrapped round an ear"""
    m = '%d_leaf' % n
    spec = [((2, 4), (8, 12)), ((8, 7), (12, 14)), ((12, 10), (15, 16))][:layers]
    els = []
    for (y0, z0), (y1, z1) in spec:
        els.append(block((-2, y0, z0), (0, y1, z1), m))
        els.append(block((16, y0, z0), (18, y1, z1), m))
    return els


def neck(n):
    return [block((-1, 0, 16), (17, 4, 18), '%d_plate' % n)]


def crest_seed(n):
    """a seam over the crown, a two-pixel shoot breaking out of it at the front"""
    return [block((7, 16, 4), (9, 17, 15), '%d_plate' % n),
            block((7, 16, 1), (9, 19, 3), '%d_leaf' % n), block((9, 18, 1), (11, 19, 3), '%d_leaf' % n)]


def crest_wheat(n):
    """a wheat ear laid along the crown: kernels alternating either side of the stalk, the tip rising at the front"""
    m = '%d_grain' % n
    els = [block((7, 16, 0), (9, 19, 2), m)]
    for i, z in enumerate(range(2, 15, 2)):
        x = 6 if i % 2 == 0 else 8
        els.append(block((x, 16, z), (x + 2, 18 if z < 10 else 17, z + 2), m))
    return els


def crest_sheaf(n):
    """three bound stalks running over the crown, held by a bronze band"""
    g = '%d_grain' % n
    return [block((5, 16, 2), (7, 17, 15), g), block((7, 16, 1), (9, 18, 15), g), block((9, 16, 2), (11, 17, 15), g),
            block((4, 16, 7), (12, 19, 9), '%d_blade' % n)]


def crest_scythe(n):
    """a scythe blade rising from the back of the crown and curving forward over the brow"""
    m = '%d_blade' % n
    return [block((7, 16, 10), (9, 19, 15), m), block((7, 18, 6), (9, 21, 11), m), block((7, 20, 2), (9, 22, 7), m),
            block((7, 19, -2), (9, 21, 3), m), block((7, 17, -4), (9, 19, 0), m)]


def crest_leaf(n):
    """a single great leaf blade along the crown, stepping up to its tip"""
    m = '%d_leaf' % n
    return [block((7, 16, 1), (9, 18, 15), m), block((7, 18, 3), (9, 20, 12), m), block((7, 20, 5), (9, 21, 9), m)]


def rune(n):
    """a gold seed set into the centre of the brow, faintly lit"""
    return [block((7, 14, -5), (9, 16, -4), '%d_grain' % n),
            {'from': [7.4, 14.4, -5.05], 'to': [8.6, 15.6, -5.05], 'light_emission': 10,
             'faces': {'north': {'uv': uv_px('%d_eye' % n, 1, 1), 'texture': '#0'}}}]


M = {
    1: head(1) + leaf_brow(1) + husk(1, 1) + crest_seed(1),
    2: head(2) + sickle_brow(2) + husk(2, 2) + crest_wheat(2),
    3: head(3) + sickle_brow(3) + husk(3, 2) + neck(3) + crest_sheaf(3),
    4: head(4) + sickle_brow(4) + husk(4, 2) + neck(4) + crest_scythe(4),
    5: head(5) + sickle_brow(5, lift=2) + husk(5, 3) + neck(5) + crest_leaf(5) + rune(5),
}


def model(elements):
    return {
        'texture_size': [T, T],
        'textures': {'0': 'elytro:item/farm_caps', 'particle': 'elytro:item/farm_caps'},
        'elements': elements,
        'gui_light': 'front',      # lit evenly from the viewer, so the face reads in a slot instead of going dark
        'display': {
            'gui': {'rotation': [18, 162, 0], 'translation': [0, -0.5, 0], 'scale': [0.52, 0.52, 0.52]},
            'ground': {'translation': [0, 2, 0], 'scale': [0.3, 0.3, 0.3]},
            'fixed': {'rotation': [0, 180, 0], 'scale': [0.55, 0.55, 0.55]},
            'thirdperson_righthand': {'rotation': [75, 45, 0], 'translation': [0, 1, 1], 'scale': [0.3, 0.3, 0.3]},
            'thirdperson_lefthand': {'rotation': [75, 45, 0], 'translation': [0, 1, 1], 'scale': [0.3, 0.3, 0.3]},
            'firstperson_righthand': {'rotation': [0, 135, 0], 'translation': [0, 1, 0], 'scale': [0.3, 0.3, 0.3]},
            'firstperson_lefthand': {'rotation': [0, 135, 0], 'translation': [0, 1, 0], 'scale': [0.3, 0.3, 0.3]},
        },
    }


for n, els in M.items():
    p = os.path.join(OUT, 'models', 'item')
    os.makedirs(p, exist_ok=True)
    json.dump(model(els), open(os.path.join(p, 'farm_cap_%d.json' % n), 'w'), indent=1)
    p = os.path.join(OUT, 'items')
    os.makedirs(p, exist_ok=True)
    json.dump({'model': {'type': 'minecraft:model', 'model': 'elytro:item/farm_cap_%d' % n}},
              open(os.path.join(p, 'farm_cap_%d.json' % n), 'w'), indent=1)
print('built', {n: len(e) for n, e in M.items()})
