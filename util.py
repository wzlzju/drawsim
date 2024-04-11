import os


def addImgExt(path):
    imgext = [".png", ".PNG", ".jpg", ".jpeg", ".JPG", ".bmp", ".BMP", ".webp"]
    for ext in imgext:
        imgpath = path + ext
        if os.path.exists(imgpath):
            break
        imgpath = path + ".png"
    return imgpath