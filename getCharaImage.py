import json, os, time
import requests
from fake_useragent import UserAgent

from PIL import Image
import io

from fehdata import data

headers = {"User-Agent": UserAgent().random}
def url(name):
    return "http://www.arcticsilverfox.com/feh_sim/heroes/%s.png" % name

def crawl():
    for i, hero in enumerate(data["heroes"]):
        name = hero["name"]
        try:
            chpath = "./img/chara/%s.png" % name
            if not os.path.exists(chpath):
                img_bin = requests.get(url=url(name),headers=headers).content
                img=Image.open(io.BytesIO(img_bin))
                img = img.resize((60, 60))
                img.save(chpath)
                print(i, name)
                time.sleep(0.1)
        except:
            print("ERROR", name)



if __name__ == "__main__":
    crawl()