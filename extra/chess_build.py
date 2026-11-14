"""Native Minecraft cuboid models: one table display and one display per piece."""
from pathlib import Path
import json, zipfile

ROOT = Path(__file__).resolve().parent
ASSETS = ROOT / "assets" / "elytro"
FACES = ["north", "south", "east", "west", "up", "down"]

def box(elements, start, end, texture="body", rotation=None):
    element = {"from": list(start), "to": list(end), "faces": {f: {"texture": "#" + texture} for f in FACES}}
    if rotation: element["rotation"] = rotation
    elements.append(element)

def save(name, elements, textures, table=False):
    display = {"gui": {"rotation": [25, 35, 0], "translation": [0, 1, 0], "scale": [.65, .65, .65]},
               "ground": {"translation": [0, 2, 0], "scale": [.4, .4, .4]},
               "firstperson_righthand": {"rotation": [0, 135, 0], "translation": [0, 2, 0], "scale": [.5, .5, .5]}}
    model = {"ambientocclusion": True, "gui_light": "front", "textures": textures,
             "display": display, "elements": elements}
    path = ASSETS / "models" / "item" / "chess" / (name + ".json")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(model, separators=(",", ":")), encoding="utf8")
    path = ASSETS / "items" / ("chess_" + name + ".json")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps({"model": {"type": "minecraft:model", "model": "elytro:item/chess/" + name}}, separators=(",", ":")), encoding="utf8")

def table():
    e=[]
    for x in [1.8,12.7]:
        for z in [1.8,12.7]:
            box(e,(x,-1.28,z),(x+1.5,13.8,z+1.5),"wood")
            box(e,(x-.15,-1.28,z-.15),(x+1.65,.25,z+1.65),"gold")
    box(e,(0,13.8,0),(16,15.3,16),"wood")
    for x in [.7,14.9]: box(e,(x,15.3,.7),(x+.4,15.55,15.3),"gold")
    for z in [.7,14.9]: box(e,(.7,15.3,z),(15.3,15.55,z+.4),"gold")
    for rank in range(8):
        for file in range(8):
            x=1.6+file*1.6;z=1.6+(7-rank)*1.6
            box(e,(x,15.3,z),(x+1.6,16,z+1.6),"dark" if (rank+file)%2==0 else "light")
    # Matching seats and high backs. The open side always faces the board.
    for sign in [-1,1]:
        cz=8+sign*2.05/3*16
        box(e,(5.5,6.5,cz-2.5),(10.5,8,cz+2.5),"wood")
        box(e,(5.8,8,cz-2.2),(10.2,8.4,cz+2.2),"cushion")
        back=cz+sign*2.05
        box(e,(5.5,8,back-.45),(10.5,16.8,back+.45),"wood")
        box(e,(5.9,9,back-.5),(10.1,16,back+.5),"cushion")
        box(e,(5.4,16.8,back-.55),(10.6,17.4,back+.55),"gold")
        for x in [5.8,9.5]:
            for z in [cz-2.15,cz+1.45]: box(e,(x,-1.28,z),(x+.7,6.5,z+.7),"wood")
    save("table",e,{"wood":"minecraft:block/dark_oak_planks","gold":"minecraft:block/gold_block",
         "light":"minecraft:block/quartz_block_top","dark":"minecraft:block/deepslate_tiles","cushion":"minecraft:block/purple_wool"},True)

def piece(side,kind):
    e=[]
    box(e,(2,0,2),(14,1.4,14)); box(e,(3,1.4,3),(13,2.3,13),"trim");box(e,(4,2.3,4),(12,3.8,12))
    if kind=="pawn":
        box(e,(5.6,3.8,5.6),(10.4,8.3,10.4));box(e,(4.6,8,4.6),(11.4,9.3,11.4),"trim");box(e,(5,9.3,5),(11,13.2,11))
    elif kind=="rook":
        box(e,(4.6,3.8,4.6),(11.4,10.6,11.4));box(e,(3.5,10.6,3.5),(12.5,12,12.5),"trim")
        for x in [3.5,9.6]:
            for z in [3.5,9.6]:box(e,(x,12,z),(x+2.9,15,z+2.9))
    elif kind=="knight":
        box(e,(4.8,3.8,5.2),(11.2,9.5,11.2));box(e,(5,8.4,6),(11,14,11),rotation={"origin":[8,8,8],"axis":"x","angle":-22.5})
        box(e,(4.7,11.5,2.8),(11.3,15,9.5));box(e,(4.7,10.2,1.5),(11.3,12.5,5))
        box(e,(5,8.5,10.5),(11,14.8,11.7),"trim")
        for x in [5,9.5]:box(e,(x,15,7),(x+1.5,17,9))
        for x in [4.55,11.05]:box(e,(x,12.8,4.5),(x+.4,13.7,5.3),"eye")
    else:
        box(e,(5.4,3.8,5.4),(10.6,9,10.6));box(e,(4.2,8.8,4.2),(11.8,10.2,11.8),"trim")
        if kind=="bishop":
            box(e,(5,10.2,5),(11,13.8,11));box(e,(6,13.8,6),(10,15.8,10))
            box(e,(7,10.1,4.85),(7.8,14.2,5.05),"trim")
        elif kind=="queen":
            box(e,(4.3,10.2,4.3),(11.7,12.1,11.7));box(e,(3.7,12.1,3.7),(12.3,13.2,12.3),"trim")
            for x,z in [(3.7,3.7),(10.3,3.7),(3.7,10.3),(10.3,10.3)]:box(e,(x,13.2,z),(x+2,16,z+2))
            box(e,(6.5,13.2,6.5),(9.5,16.6,9.5),"trim")
        else:
            box(e,(4.8,10.2,4.8),(11.2,12.4,11.2));box(e,(5.3,12.4,5.3),(10.7,13.4,10.7),"trim")
            box(e,(6.7,13.4,6.7),(9.3,18.3,9.3));box(e,(4.4,15.1,6.7),(11.6,17,9.3),"trim")
    save(side+"_"+kind,e,{"body":"minecraft:block/quartz_block_side" if side=="white" else "minecraft:block/polished_blackstone",
          "trim":"minecraft:block/gold_block" if side=="white" else "minecraft:block/amethyst_block",
          "eye":"minecraft:block/polished_blackstone" if side=="white" else "minecraft:block/gold_block"})

if __name__=="__main__":
    table()
    for side in ["white","black"]:
        for kind in ["pawn","rook","knight","bishop","queen","king"]:piece(side,kind)
    files=list((ASSETS/"models/item/chess").glob("*.json"))+list((ASSETS/"items").glob("chess_*.json"));assert len(files)==26
    for file in files:
        model=json.loads(file.read_text())
        for part in model.get("elements",[]):
            assert all(-16 <= n <= 32 for n in part["from"]+part["to"]),file
            assert all(a<b for a,b in zip(part["from"],part["to"])),file
    print("Built",len(files),"chess model/item definitions")
