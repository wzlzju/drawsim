import json, os, time
import requests
from fake_useragent import UserAgent

from PIL import Image
import io
from util import *

headers = {"User-Agent": UserAgent().random}
def url(name):
    return "http://www.arcticsilverfox.com/feh_sim/heroes/%s.png" % name

def crawl():
    # from fehdata import data
    from tmpdata import data

    imgpath = "./img/chara/"
    if not os.path.exists(imgpath):
        os.makedirs(imgpath)
    for i, hero in enumerate(data["heroes"]):
        name = hero["name"]
        try:
            chpath = imgpath + "%s.png" % name
            if not os.path.exists(chpath):
                img_bin = requests.get(url=url(name),headers=headers).content
                img=Image.open(io.BytesIO(img_bin))
                img = img.resize((60, 60))
                img.save(chpath)
                print(i, name)
                time.sleep(0.1)
        except:
            print("ERROR", name, link_to)

def update():
    url = "http://www.arcticsilverfox.com/score_calc/"
    data = requests.get(url=url,headers=headers).content.decode("utf-8")
    data = data.split("<script>\n\t\tvar data = {};\n\t\t")[1].split("\t</script>")[0]
    data = data.replace("data.heroes", 'data["heroes"]')
    data = data.replace("data.skills", 'data["skills"]')
    data = data.replace("data.prereqs", 'data["prereqs"]')
    data = data.replace("data.heroSkills", 'data["heroSkills"]')
    data = data.replace("data.prfSkills", 'data["prfSkills"]')
    for _ in range(5):
        data = data.replace("\t\t", '\n')
        data = data.replace("}];\n", '}]\n\n')
    data = 'null = None\nSPECIAL_4TO5_VER = "4.11"\n\ndata = {}\ndata["special_4to5_version"] = SPECIAL_4TO5_VER\n\n'+data
    with open("tmpdata.py", "w") as f:
        f.write(data)


if __name__ == "__main__":
    update()
    crawl()
