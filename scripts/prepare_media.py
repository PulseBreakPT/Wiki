"""Create responsive derivatives of a small selection of official promotional media.
Original gallery: https://www.rockstargames.com/VI/media/screenshots
Copyright remains with Rockstar Games; no open license is asserted.
"""
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
from io import BytesIO
import requests
from PIL import Image, ImageOps, ImageDraw

BASE='https://www.rockstargames.com/VI/_next/static/media/'
IMAGES={
  'jason':'Jason_Duval_01.07m377xeb6jhq.jpg',
  'lucia':'Lucia_Caminos_01.0a7yqvewctkfp.jpg',
  'vice-city':'Vice_City_01.135x56yoeu.6t.jpg',
  'hero':'Vice_City_02.0c5.7qx17u9kl.jpg',
  'hero-alternative':'Vice_City_09.0~ng.c8ack3fp.jpg',
  'hero-night':'Vice_City_04.06evqutgh7624.jpg',
  'hero-sunset':'Vice_City_06.0_tdmr3u9w84x.jpg',
  'hero-city':'Vice_City_08.0bbg_xp4hqdvz.jpg',
  'keys':'Leonida_Keys_01.0zgz7tveur6y8.jpg',
  'cal':'Cal_Hampton_01.0xlil231_osh4.jpg',
  'brian':'Brian_Heder_01.0r.ute88os9k-.jpg',
  'boobie':'Boobie_Ike_01.0-wji2pg5anfs.jpg',
  'grassrivers':'Grassrivers_01.1096rw4lbjur_.jpg',
  'port':'Port_Gellhorn_01.0fmisvza-5-cq.jpg',
  'ambrosia':'Ambrosia_01.0rqphs0gazkm..jpg',
  'kalaga':'Mount_Kalaga_National_Park_01.0v5fl0f83hjv_.jpg',
}
DEST=Path('/app/frontend/public/media')
DEST.mkdir(parents=True,exist_ok=True)

def download(item):
    name,file=item
    if (DEST/f'{name}.webp').exists():
        return name,Image.open(DEST/f'{name}.webp').convert('RGB')
    response=requests.get(BASE+file+'?imwidth=1920',timeout=50)
    response.raise_for_status()
    image=Image.open(BytesIO(response.content)).convert('RGB')
    image.thumbnail((1920,1080) if name.startswith('hero') else (1200,800))
    image.save(DEST/f'{name}.webp','WEBP',quality=85)
    print(name,image.size)
    return name,image

if __name__=='__main__':
    results=list(ThreadPoolExecutor(max_workers=6).map(download, IMAGES.items()))
    sheet=Image.new('RGB',(1000,230*((len(results)+2)//3)), '#0a0b10')
    draw=ImageDraw.Draw(sheet)
    for i,(name,image) in enumerate(results):
        x,y=(i%3)*333,(i//3)*230
        sheet.paste(ImageOps.fit(image,(325,190)),(x,y))
        draw.text((x+6,y+195),name,fill='white')
    sheet.save('/app/media-contact-sheet.jpg')