"""Album covers for the Elytro music library -> resource pack assets.
Usage: python -I build_covers.py <dir with <id>.jpg> <catalog.json> <assets out> <preview.png>
Writes elytro:item/cover/<id> textures + models + item definitions, and an override of
elytromusic:items/cd.json that shows each CD's cover (select on its custom_data track id)."""
import json, math, os, sys
from PIL import Image, ImageDraw, ImageFont, ImageFilter

SRC, CAT, OUT, PREV = sys.argv[1:5]
tracks = json.load(open(CAT, encoding='utf-8'))['tracks']
TEX = os.path.join(OUT, 'elytro', 'textures', 'item', 'cover')
MOD = os.path.join(OUT, 'elytro', 'models', 'item', 'cover')
ITM = os.path.join(OUT, 'elytro', 'items', 'cover')
MITM = os.path.join(OUT, 'elytromusic', 'items')
for d in (TEX, MOD, ITM, MITM):
    os.makedirs(d, exist_ok=True)
S = 128


def framed(img):
    img = img.convert('RGB').resize((S - 4, S - 4), Image.LANCZOS)
    out = Image.new('RGBA', (S, S), (18, 16, 24, 255))
    out.paste(img, (2, 2))
    return out


def generated(title, artist, seed):
    # Elytro-style cover for tracks with no official art: purple gradient, a vinyl, the title
    img = Image.new('RGB', (S, S))
    px = img.load()
    hues = [(76, 36, 120), (120, 44, 140), (40, 60, 130), (130, 60, 40), (30, 100, 110)]
    a, b = hues[seed % len(hues)], (14, 10, 22)
    for y in range(S):
        for x in range(S):
            t = min(1, (x + y) / (2 * S) * 1.3)
            px[x, y] = tuple(int(a[i] * (1 - t) + b[i] * t) for i in range(3))
    d = ImageDraw.Draw(img)
    cx, cy, r = 92, 40, 30
    d.ellipse((cx - r, cy - r, cx + r, cy + r), fill=(16, 16, 18))
    for rr in range(10, r, 4):
        d.ellipse((cx - rr, cy - rr, cx + rr, cy + rr), outline=(34, 34, 40))
    d.ellipse((cx - 9, cy - 9, cx + 9, cy + 9), fill=(214, 170, 72))
    d.ellipse((cx - 2, cy - 2, cx + 2, cy + 2), fill=(10, 10, 12))
    try:
        font = ImageFont.truetype('C:/Windows/Fonts/arialbd.ttf', 15)
        small = ImageFont.truetype('C:/Windows/Fonts/arial.ttf', 11)
    except Exception:
        font = small = ImageFont.load_default()
    words, lines = title.split(), ['']
    for w in words:
        if d.textlength((lines[-1] + ' ' + w).strip(), font=font) > S - 16 and lines[-1]:
            lines.append(w)
        else:
            lines[-1] = (lines[-1] + ' ' + w).strip()
    lines = lines[:3]
    y = S - 14 - 17 * len(lines) - 12
    for ln in lines:
        d.text((9, y), ln, font=font, fill=(245, 240, 250))
        y += 17
    d.text((9, y + 2), artist[:22], font=small, fill=(200, 190, 215))
    return framed(img)


def clean(s):
    import re
    s = re.sub(r'\((?:feat|with|prod)[^)]*\)|\[[^\]]*\]|\(extended\)|\(unreleased\)', '', s, flags=re.I)
    s = re.sub(r'^.*? - ', '', s) if ' - ' in s else s
    return ' '.join(s.replace('Travi$', 'Travis').split())


covers = []
previews = []
for i, (tid, t) in enumerate(tracks.items()):
    jpg = os.path.join(SRC, tid + '.jpg')
    if os.path.exists(jpg):
        img = framed(Image.open(jpg))
    else:
        title = clean(t['title']) or t['title']
        artist = t.get('artist', 'Elytro')
        names = {
            'elytro_soundcheck': ('SOUND CHECK', 'Elytro'),
            'diplo_wish': ('WISH', 'Diplo ft. Trippie Redd'),
            'travi_scott_bad_mood_shit_on_you_malluminati': ('Bad Mood / Shit On You', 'Travis Scott'),
            'unreleased_no_vancancy_travis_scott_feat_21_sava': ('NO VACANCY', 'Travis Scott ft. 21 Savage'),
            'playboi_carti_shoota_feat_lil_uzi_vert_extended': ('SHOOTA', 'Playboi Carti ft. Lil Uzi Vert'),
        }
        if tid in names:
            title, artist = names[tid]
        img = generated(title, artist, i)
    img.save(os.path.join(TEX, tid + '.png'))
    json.dump({'parent': 'minecraft:item/generated', 'textures': {'layer0': 'elytro:item/cover/' + tid}},
              open(os.path.join(MOD, tid + '.json'), 'w'), indent=1)
    json.dump({'model': {'type': 'minecraft:model', 'model': 'elytro:item/cover/' + tid}},
              open(os.path.join(ITM, tid + '.json'), 'w'), indent=1)
    covers.append(tid)
    previews.append(img)

# CDs (elytromusic:cd, set by music_manager.sk) show their track's cover; unknown tracks keep the plain CD
cases = [{'when': {'PublicBukkitValues': {'elytromusic:track': tid}},
          'model': {'type': 'minecraft:model', 'model': 'elytro:item/cover/' + tid}} for tid in covers]
json.dump({'model': {'type': 'minecraft:select', 'property': 'minecraft:component', 'component': 'minecraft:custom_data',
                     'cases': cases, 'fallback': {'type': 'minecraft:model', 'model': 'elytromusic:item/cd'}}},
          open(os.path.join(MITM, 'cd.json'), 'w'), indent=1)
json.dump(covers, open(os.path.join(OUT, '..', 'covers.json'), 'w'))

cols = 5
sheet = Image.new('RGBA', (cols * (S + 8), math.ceil(len(previews) / cols) * (S + 8)), (40, 36, 48, 255))
for i, im in enumerate(previews):
    sheet.paste(im, ((i % cols) * (S + 8) + 4, (i // cols) * (S + 8) + 4))
sheet.save(PREV)
print(len(covers), 'covers')
