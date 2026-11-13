"""Vaus's Chestplate Mk I..VII, round 9 (2026-11-12): the farm helmets' treatment on a real chestplate.

nikoc: "give them the same treatment you gave helmets in farming. Same overall theme,
progression line". Base: the vanilla iron chestplate (icon + humanoid layer, vanilla
resolution). Like the helms (extra/farm_helms_build.py), farming is built into the
construction rather than glued on: a plant stem runs down the chest as the centre ridge and
feeds leaf veins engraved across the chest, the collar is a sickle crescent, the shoulders
wrap in layered husk plates, and each Mk carries a crop or tool as its chest emblem (the
helms' crest). Each Mk uses the shell palette of the Farm Armor tier it counts as
(FarmArmor config marrow marks: tiers 1,2,2,3,4,4,5), from the helms' own TIERS:
  I    Sprout     olive husk shell, a leaf collar, a seed shoot, one husk layer
  II   Harvester  straw-gold shell, bronze sickle collar, a wheat ear, one husk layer
  III  Harvester  + a second husk layer, two wheat ears, a bronze waist guard
  IV   Thresher   dark oak and bronze, three bound stalks, two husk layers, waist guard
  V    Reaper     plum iron, steel sickle collar, a scythe, two husk layers
  VI   Reaper     + a third husk layer, faint light in the leaf veins
  VII  Verdant    forest green and aged gold, a great leaf with a lit gold seed, gold
                  collar, three husk layers, light in the veins
The magic stays small, as on the helms: only VI and VII have any light.
Usage: python -I vaus_helmline_build.py <vanilla dir> <assets out dir> <preview.png>
"""
import json, os, sys
from PIL import Image


def hexc(s):
    return tuple(int(s[i:i + 2], 16) for i in (1, 3, 5))


# the helms' TIERS (extra/farm_helms_build.py)
TIERS = {
    1: dict(shell=('#34341E', '#46462A', '#5A5934', '#706E40', '#86844E'), leaf=('#3C5E22', '#527A2C', '#6C9838'),
            blade=('#6E5428', '#8E6E36', '#B8945A'), grain=('#B89A48', '#D6B86A'), k='#121208', e='#A6F07A'),
    2: dict(shell=('#4A3A1C', '#5E4A24', '#76602E', '#8E7638', '#A88E46'), leaf=('#4A5E24', '#5E762E', '#76903A'),
            blade=('#7A5A26', '#A07A36', '#D0A858'), grain=('#C49A3C', '#E6C468'), k='#140E06', e='#FFC25A'),
    # nikoc 2026-11-12: the helms' orange (Thresher) and purple (Reaper) shells clash with the
    # green on a chestplate, so these two are moss iron and blue steel instead
    3: dict(shell=('#2A2E24', '#383D30', '#484E3E', '#5A614E', '#6E7660'), leaf=('#40582A', '#546E34', '#6A8840'),
            blade=('#7A6430', '#A08440', '#CCAC5C'), grain=('#B89A48', '#D8BC6A'), k='#0E100A', e='#A6F07A'),
    4: dict(shell=('#1E2428', '#283036', '#343E46', '#424E58', '#54626E'), leaf=('#365430', '#48703C', '#5E8C4A'),
            blade=('#6E7680', '#9AA2AC', '#D2D8E0'), grain=('#9AA2AC', '#D2D8E0'), k='#0A0C10', e='#A6F0A0'),
    5: dict(shell=('#142A1C', '#1C3A26', '#264A30', '#305C3A', '#3E7046'), leaf=('#2E5E2A', '#3E7A34', '#56963E'),
            blade=('#7A5C24', '#A68236', '#D6B05A'), grain=('#E0BC5C', '#FFE09A'), k='#08120C', e='#A6F0A0'),
}
MK_TIER = {1: 1, 2: 2, 3: 2, 4: 3, 5: 4, 6: 4, 7: 5}


def pal(mk):
    t = TIERS[MK_TIER[mk]]
    p = {f's{i}': hexc(c) for i, c in enumerate(t['shell'])}
    p.update(a=hexc(t['leaf'][0]), b=hexc(t['leaf'][1]), c=hexc(t['leaf'][2]),
             x=hexc(t['blade'][0]), y=hexc(t['blade'][1]), z=hexc(t['blade'][2]),
             g=hexc(t['grain'][0]), h=hexc(t['grain'][1]), k=hexc(t['k']), e=hexc(t['e']))
    return p


def recolour(img, p, outline=None):
    """Vanilla iron -> the tier's shell ramp, keeping vanilla's own shading."""
    out = img.copy()
    px = out.load()
    ramp = [p['s0'], p['s1'], p['s2'], p['s3'], p['s4']]
    for yy in range(out.height):
        for xx in range(out.width):
            r, g, b, a = px[xx, yy]
            if a == 0:
                continue
            l = (r * 299 + g * 587 + b * 114) / 1000
            if l < 60:
                c = outline or p['k']
            else:
                t = max(0.0, min(1.0, (l - 90) / (235 - 90))) * 4
                i = min(int(t), 3)
                f = t - i
                c = tuple(int(ramp[i][j] + (ramp[i + 1][j] - ramp[i][j]) * f) for j in range(3))
            px[xx, yy] = c + (a,)
    return out


class Paint:
    """Paints only onto pixels the vanilla texture already has."""

    def __init__(self, img, ox=0, oy=0):
        self.img, self.px, self.ox, self.oy = img, img.load(), ox, oy

    def s(self, x, y, c):
        x += self.ox; y += self.oy
        if 0 <= x < self.img.width and 0 <= y < self.img.height and self.px[x, y][3] > 0:
            self.px[x, y] = tuple(c[:3]) + (255,)

    def pts(self, cells, c):
        for (x, y) in cells:
            self.s(x, y, c)


def shade(c, f):
    return tuple(max(0, min(255, int(v * f))) for v in c[:3])


def folds(im, ox, oy, w, rows, skip=()):
    """Layered folds: on each fold row the plate edge above catches the light and the row
    under it sits in shadow, so the armour reads as overlapping layers."""
    px = im.load()
    for r in rows:
        for x in range(w):
            if x in skip:
                continue
            for (yy, f) in ((r - 1, 1.18), (r, 0.62)):
                X, Y = ox + x, oy + yy
                if 0 <= X < im.width and 0 <= Y < im.height and px[X, Y][3] > 0:
                    c = px[X, Y]
                    px[X, Y] = shade(c, f) + (c[3],)


def core(p, P, mk, cx, cy):
    """The core the stem grows from: a 2x2 gem in a bezel of the blade metal."""
    P.pts([(cx - 1, cy), (cx - 1, cy + 1), (cx + 2, cy), (cx + 2, cy + 1)], p['y'] if mk < 7 else p['g'])
    if mk == 1:
        P.pts([(cx, cy), (cx + 1, cy), (cx + 1, cy + 1)], p['k'])
        P.s(cx, cy + 1, p['a'])
        return
    lit = p['e']
    if mk == 2:
        dim = shade(lit, 0.55)
        P.pts([(cx, cy), (cx + 1, cy), (cx, cy + 1), (cx + 1, cy + 1)], p['k'])
        P.s(cx, cy, dim)
        return
    hi = tuple(min(255, v + 70) for v in lit)
    P.s(cx, cy, hi); P.s(cx + 1, cy, lit); P.s(cx, cy + 1, lit); P.s(cx + 1, cy + 1, shade(lit, 0.6))
    if mk >= 6:
        # a faint halo on the bezel
        P.pts([(cx - 1, cy), (cx + 2, cy)], shade(lit, 0.8))


def emblem(p, P, mk, cx, top):
    """The chest emblem (the helms' crest) on a stem; cx = left of the 2-wide centre, top =
    the emblem's top row. Drawn in local coordinates of P."""
    # the stem: the centre ridge, down to the waist
    for yy in range(top + 2, top + 9):
        P.s(cx, yy, p['b']); P.s(cx + 1, yy, p['a'])
    if mk == 1:                                    # a seed shoot
        P.pts([(cx, top + 1), (cx + 1, top + 1)], p['c'])
        P.pts([(cx - 1, top + 2), (cx + 2, top + 2)], p['c'])
        P.s(cx, top, p['c'])
    elif mk in (2, 3):                             # a wheat ear (two from III)
        for i in range(4):
            P.s(cx, top + i, p['h'] if i % 2 == 0 else p['g'])
            P.s(cx + 1, top + i, p['g'] if i % 2 == 0 else p['h'])
        P.pts([(cx - 1, top), (cx + 2, top)], p['h'])
        if mk == 3:
            P.pts([(cx - 2, top + 1), (cx - 2, top + 3), (cx + 3, top + 1), (cx + 3, top + 3)], p['g'])
            P.pts([(cx - 2, top + 2), (cx + 3, top + 2)], p['h'])
    elif mk == 4:                                  # three bound stalks
        for xx in (cx - 2, cx, cx + 1, cx + 3):
            for i in range(4):
                P.s(xx, top + i, p['h'] if i == 0 else p['g'])
        P.pts([(xx, top + 3) for xx in range(cx - 2, cx + 4)], p['y'])
    elif mk in (5, 6):                             # a scythe on its haft
        P.pts([(cx - 2, top + 1), (cx - 1, top), (cx, top), (cx + 1, top), (cx + 2, top)], p['z'])
        P.pts([(cx + 3, top + 1)], p['y'])
        P.pts([(cx - 2, top + 2)], p['x'])
        for yy in range(top + 1, top + 8):
            P.s(cx + 1, yy, p['x'])
    else:                                          # a great leaf with a lit gold seed
        P.pts([(cx, top), (cx + 1, top)], p['c'])
        P.pts([(cx - 1, top + 1), (cx + 2, top + 1), (cx - 2, top + 2), (cx + 3, top + 2),
               (cx - 2, top + 3), (cx + 3, top + 3), (cx - 1, top + 4), (cx + 2, top + 4)], p['c'])
        P.pts([(cx - 1, top + 2), (cx + 2, top + 2), (cx - 1, top + 3), (cx + 2, top + 3)], p['b'])
        P.pts([(cx, top + 1), (cx + 1, top + 1), (cx, top + 4), (cx + 1, top + 4)], p['b'])
        P.pts([(cx, top + 2), (cx + 1, top + 2)], p['h'])        # the seed
        P.pts([(cx, top + 3), (cx + 1, top + 3)], p['e'])


def worn(base, mk):
    p = pal(mk)
    im = recolour(base, p)
    # layered folds (before any painting): abdomen, back, sides
    folds(im, 20, 20, 8, (8, 10))
    folds(im, 32, 20, 8, (4, 8, 10))
    folds(im, 16, 20, 4, (4, 8, 10)); folds(im, 28, 20, 4, (4, 8, 10))
    F = Paint(im, 20, 20)          # body front, 8 x 12
    # collar: a leaf collar on Mk I, a sickle crescent after (gold on VII)
    col_hi, col_lo = (p['c'], p['b']) if mk == 1 else ((p['h'], p['g']) if mk == 7 else (p['z'], p['y']))
    F.pts([(0, 0), (1, 0), (6, 0), (7, 0)], col_hi)
    F.pts([(1, 1), (2, 1), (5, 1), (6, 1)], col_lo)
    # leaf veins engraved across the chest, feeding off the stem (lit on VI, VII)
    vein = p['e'] if mk >= 6 else p['a']
    F.pts([(2, 3), (1, 2), (5, 3), (6, 2), (2, 6), (1, 5), (5, 6), (6, 5)], vein)
    emblem(p, F, mk, 3, 2)
    core(p, F, mk, 3, 6)
    # waist: a bronze guard from III
    if mk >= 3:
        F.pts([(xx, 11) for xx in range(8)], p['y'] if mk < 7 else p['g'])
    # back (x 32..39): the stem ridge, veins, a husk band at the top
    B = Paint(im, 32, 20)
    for yy in range(1, 11):
        B.s(3, yy, p['b']); B.s(4, yy, p['a'])
    B.pts([(2, 3), (1, 2), (5, 3), (6, 2), (2, 7), (1, 6), (5, 7), (6, 6)], vein)
    B.pts([(xx, 0) for xx in range(8)], p['c'])
    if mk >= 3:
        B.pts([(xx, 11) for xx in range(8)], p['y'] if mk < 7 else p['g'])
    # sides (x 16..19 and 28..31): a leaf vein each
    for ox in (16, 28):
        S = Paint(im, ox, 20)
        S.pts([(1, 3), (2, 4), (1, 6), (2, 7)], p['a'] if mk < 6 else p['e'])
    # shoulders: husk plates wrapping the arm (x 40..55, y 20..31), 1 / 2 / 3 layers
    layers = 1 if mk <= 2 else (2 if mk <= 5 else 3)
    # only on the outer (x 0..3), front (4..7) and back (12..15) faces of the arm: the inner
    # face (8..11) and the top clip into the chest when the arms swing, so they stay plain shell
    A = Paint(im, 40, 20)
    faces = [xx for xx in range(16) if not 8 <= xx <= 11]
    for li in range(layers):
        y0 = li * 3
        A.pts([(xx, y0) for xx in faces], p['c'])
        A.pts([(xx, y0 + 1) for xx in faces], p['b'])
    if mk >= 7:
        A.pts([(xx, 0) for xx in faces], p['h'])
    return im


def icon(base, mk):
    p = pal(mk)
    # vanilla-style edge: a dark shade of the shell's own colour, not black
    im = recolour(base, p, outline=tuple(int(v * 0.72) for v in p['s1']))
    # layered folds across the body; the outline columns stay as they are
    folds(im, 0, 0, 16, (9, 11), skip=(0, 1, 2, 3, 12, 13, 14, 15))
    P = Paint(im)
    # collar crescent along the neck V
    col_hi, col_lo = (p['c'], p['b']) if mk == 1 else ((p['h'], p['g']) if mk == 7 else (p['z'], p['y']))
    P.pts([(5, 4), (10, 4)], col_hi)
    P.pts([(6, 5), (9, 5)], col_lo)
    # shoulders: husk layers
    layers = 1 if mk <= 2 else (2 if mk <= 5 else 3)
    rows = [3, 5, 4][:layers]
    for r in rows:
        P.pts([(2, r), (3, r), (4, r), (11, r), (12, r), (13, r)], p['c'] if r == 3 else p['b'])
    if mk >= 7:
        P.pts([(2, 3), (3, 3), (4, 3), (11, 3), (12, 3), (13, 3)], p['h'])
    # veins
    vein = p['e'] if mk >= 6 else p['a']
    P.pts([(5, 9), (4, 8), (10, 9), (11, 8)], vein)
    emblem(p, P, mk, 7, 6)
    core(p, P, mk, 7, 9)
    if mk >= 3:
        P.pts([(xx, 12) for xx in range(4, 12)], p['y'] if mk < 7 else p['g'])
    return im


def main():
    van, out_dir, preview = sys.argv[1], sys.argv[2], sys.argv[3]
    ib = Image.open(os.path.join(van, 'item_iron_chestplate.png')).convert('RGBA')
    wb = Image.open(os.path.join(van, 'humanoid_iron.png')).convert('RGBA')
    d = {k: os.path.join(out_dir, 'elytro', *k.split('/')) for k in
         ('equipment', 'textures/entity/equipment/humanoid', 'textures/item', 'models/item', 'items')}
    for q in d.values():
        os.makedirs(q, exist_ok=True)
    Z = 8
    colw = 40 * 5 + 16
    prev = Image.new('RGBA', (7 * colw + 16, 16 * Z + 24 * 5 + 50), (139, 139, 139, 255))
    for k in range(1, 8):
        w = worn(wb, k); ic = icon(ib, k)
        clean = Image.new('RGBA', w.size, (0, 0, 0, 0))
        clean.paste(w.crop((16, 16, 56, 32)), (16, 16))
        clean.save(os.path.join(d['textures/entity/equipment/humanoid'], f'vaus_mk{k}.png'))
        ic.save(os.path.join(d['textures/item'], f'vaus_mk{k}_chest.png'))
        json.dump({'layers': {'humanoid': [{'texture': f'elytro:vaus_mk{k}'}]}},
                  open(os.path.join(d['equipment'], f'vaus_mk{k}.json'), 'w'), indent=2)
        json.dump({'parent': 'minecraft:item/generated', 'textures': {'layer0': f'elytro:item/vaus_mk{k}_chest'}},
                  open(os.path.join(d['models/item'], f'vaus_mk{k}_chest.json'), 'w'), indent=2)
        json.dump({'model': {'type': 'minecraft:model', 'model': f'elytro:item/vaus_mk{k}_chest'}},
                  open(os.path.join(d['items'], f'vaus_mk{k}_chest.json'), 'w'), indent=2)
        x = 16 + (k - 1) * colw
        big = ic.resize((16 * Z, 16 * Z), Image.NEAREST)
        prev.paste(big, (x + 40, 10), big)
        # worn preview: arm | front | arm, then back
        def crop(a, b, w_, h_):
            return clean.crop((a, b, a + w_, b + h_))
        doll = Image.new('RGBA', (16, 12), (0, 0, 0, 0))
        arm = crop(44, 20, 4, 12)
        doll.paste(arm, (0, 0), arm); doll.paste(crop(20, 20, 8, 12), (4, 0)); fl = arm.transpose(Image.FLIP_LEFT_RIGHT); doll.paste(fl, (12, 0), fl)
        dollb = Image.new('RGBA', (16, 12), (0, 0, 0, 0))
        armb = crop(52, 20, 4, 12)
        dollb.paste(armb, (0, 0), armb); dollb.paste(crop(32, 20, 8, 12), (4, 0)); flb = armb.transpose(Image.FLIP_LEFT_RIGHT); dollb.paste(flb, (12, 0), flb)
        prev.paste(doll.resize((16 * 6, 12 * 6), Image.NEAREST), (x, 16 * Z + 24), doll.resize((16 * 6, 12 * 6), Image.NEAREST))
        prev.paste(dollb.resize((16 * 6, 12 * 6), Image.NEAREST), (x + 104, 16 * Z + 24), dollb.resize((16 * 6, 12 * 6), Image.NEAREST))
    prev.save(preview)
    print('ok')


if __name__ == '__main__':
    main()
