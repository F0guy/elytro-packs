"""Original Elytro card artwork and native item models; no external artwork needed."""
from pathlib import Path
import json,zipfile
from PIL import Image,ImageDraw,ImageFont

ROOT=Path(__file__).resolve().parent
ASSETS=ROOT/'assets/elytro'
CHESS=ROOT/'assets/elytro/models/item/chess/table.json'

def write(path,data):
 path=ASSETS/path;path.parent.mkdir(parents=True,exist_ok=True);path.write_text(json.dumps(data,separators=(',',':')),encoding='utf8')
def font(size):
 for name in ['C:/Windows/Fonts/consolab.ttf','C:/Windows/Fonts/arialbd.ttf']:
  if Path(name).exists():return ImageFont.truetype(name,size)
 return ImageFont.load_default(size=size)
def text(draw,xy,value,size,fill,anchor='mm'):
 draw.text(xy,value,font=font(size),fill=fill,anchor=anchor,stroke_width=0)
def item(name,model):write(Path('items')/('uno_'+name+'.json'),{'model':{'type':'minecraft:model','model':'elytro:item/uno/'+model}})
def card(name,colour,label):
 image=Image.new('RGBA',(64,64),(0,0,0,0));d=ImageDraw.Draw(image)
 d.rounded_rectangle((12,1,52,63),radius=5,fill=(242,234,215,255));d.rounded_rectangle((14,3,50,61),radius=4,fill=colour)
 d.rounded_rectangle((17,15,47,50),radius=10,outline=(255,255,255,220),width=2)
 if name in ['wild','draw4','back']:
  for box,c in [((18,16,31,31),'#d84643'),((32,16,45,31),'#e6be38'),((18,32,31,47),'#51ad69'),((32,32,45,47),'#4b9adb')]:d.rounded_rectangle(box,radius=3,fill=c)
  d.rounded_rectangle((19,25,45,40),radius=3,fill=(25,23,36,255));text(d,(32,32),'ELY' if name=='back' else '+4' if name=='draw4' else 'W',13,'#fff5df')
 else:text(d,(32,32),label,20 if len(label)<2 else 16,'#fff7e6')
 small='ELY' if name=='back' else label
 text(d,(18,9),small,7,'#fff7e6',anchor='mm');text(d,(45,55),small,7,'#fff7e6',anchor='mm')
 path=ASSETS/'textures/item/uno'/f'{name}.png';path.parent.mkdir(parents=True,exist_ok=True);image.save(path)
 write(Path('models/item/uno')/(name+'.json'),{'parent':'minecraft:item/generated','textures':{'layer0':'elytro:item/uno/'+name}});item(name,name)
def table():
 old=json.loads(CHESS.read_text());parts=[e for e in old['elements'] if next(iter(e['faces'].values()))['texture'] not in ['#light','#dark']]
 chairs=[e for e in parts if e['from'][2]<0 or e['to'][2]>16]
 for source in chairs:
  e=json.loads(json.dumps(source));lo=e['from'];hi=e['to'];e['from']=[16-hi[2],lo[1],lo[0]];e['to']=[16-lo[2],hi[1],hi[0]];parts.append(e)
 parts.append({'from':[1.6,15.3,1.6],'to':[14.4,16,14.4],'faces':{f:{'texture':'#felt'} for f in ['up','down','north','south','east','west']}})
 old['elements']=parts;old['textures']['felt']='minecraft:block/green_wool';old['textures']['cushion']='minecraft:block/red_wool';old['textures'].pop('dark');old['textures'].pop('light')
 write(Path('models/item/uno/table.json'),old);item('table','table')
if __name__=='__main__':
 for name,c in [('red','#cb424c'),('yellow','#d5a72d'),('green','#359266'),('blue','#347dc2')]:
  for value in range(10):card(name+'_'+str(value),c,str(value))
  for value,label in [('skip','X'),('reverse','<>'),('draw2','+2')]:card(name+'_'+value,c,label)
 for name,label in [('wild','W'),('draw4','+4'),('back','ELY')]:card(name,'#282332',label)
 table()
 files=sorted(list(ASSETS.glob('items/uno_*.json'))+list(ASSETS.glob('models/item/uno/*.json'))+list(ASSETS.glob('textures/item/uno/*.png')));assert len(files)==167,len(files)
 for p in files:
  if p.suffix=='.json':
   data=json.loads(p.read_text())
   for e in data.get('elements',[]):assert all(-16<=n<=32 for n in e['from']+e['to']) and all(a<b for a,b in zip(e['from'],e['to'])),p
 print('Built',len(files),'UNO assets')
