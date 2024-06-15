from tkinter import *
from tkinter import ttk
from tkinter.constants import DISABLED, NORMAL, ACTIVE
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
import random, math, re, os, collections, copy, functools

from const import *
from util import *
try:
    from PIL import Image, ImageTk, ImageDraw, ImageFont
    import numpy as np
    NOPIL = False
except:
    NOPIL = True
try:
    # from fehdata import data
    from tmpdata import data
    NODATA = False
    name2color = {c["name"]:c["color"] for c in data["heroes"]}
except:
    NODATA = True


class Button1(object):
    def __init__(self, root, text="", image=None, height=30, width=120, command=None):
        self.height, self.width = height, width
        self.button_height, self.button_width = max(1,height-5), max(1,width-5)
        self.holder = []
        if image is None:
            image = getimage(label="util/charatemplate_bg_1star", size=(self.width, self.height))
        elif isinstance(image, int):
            image = getimage(label="util/charatemplate_bg_1star", size=(self.width, self.height))
        elif isinstance(image, str):
            image = getimage(label=image, size=(self.width, self.height))
        else:
            image = image
        self.button = Button(root, text=text, image=image, 
                            height=self.height, width=self.width,
                            command=command, borderwidth=0)
        self.button.img = image

    def grid(self, **kwargs):
        return self.button.grid(**kwargs)
    
    def pack(self, **kwargs):
        return self.button.pack(**kwargs)
    
    def config(self, **kwargs):
        return self.button.config(**kwargs)




if __name__ == "__main__":
    root = Tk()
    root.geometry('200x200+0+0')
    root.title('')

    imgholder=[]
    image="util/game8"
    size=(60,60)
    image=getimage(label=image, size=size)
    button = Button(root, image=image, command=None)
    button.pack()

    button=Button1(root)
    button.pack()
    
    root.mainloop()