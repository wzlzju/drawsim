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

import win32gui
import win32con
import win32api


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

class Button2(Button):  
    def __init__(self, master=None, **kw):  
        Button.__init__(self, master=master, **kw)  
        self._image = None  
        self._image_tk = None  
        self.config(borderwidth=0)
        self.config(highlightthickness=0)
        self.config(relief='flat')
        self.set_image("img/util/charatemplate_bg_1star.png")
  
    def set_image(self, image_path):  
        self._image = Image.open(image_path)  
        self._image_tk = ImageTk.PhotoImage(self._image)  
        self.config(image=self._image_tk)  
        self.config(width=self._image.width, height=self._image.height)
        self.config(compound='center')

class Button3(object):
    def __init__(self, root, text="", image=None, height=30, width=120, command=None):
        self.height, self.width = height, width
        # self.button_height, self.button_width = max(1,height-5), max(1,width-5)
        self.command = command
        if image is None:
            self.image = getimage(label="util/charatemplate_bg_1star", size=(self.width, self.height))
        elif isinstance(image, int):
            self.image = getimage(label="util/charatemplate_bg_1star", size=(self.width, self.height))
        elif isinstance(image, str):
            self.image = getimage(label=image, size=(self.width, self.height))
        else:
            self.image = image
        self.button = Canvas(root, bg=TRANSPARENTCOLOR, height=self.height, width=self.width, highlightthickness=0)

        def callback(event):
            self.command()
        self.button.bind("<Button-1>", callback)

        hwnd = self.button.winfo_id()
        colorkey = win32api.RGB(*hex2rgb(TRANSPARENTCOLOR)) 
        wnd_exstyle = win32gui.GetWindowLong(hwnd, win32con.GWL_EXSTYLE)
        new_exstyle = wnd_exstyle | win32con.WS_EX_LAYERED
        win32gui.SetWindowLong(hwnd,win32con.GWL_EXSTYLE,new_exstyle)
        win32gui.SetLayeredWindowAttributes(hwnd,colorkey,1,win32con.LWA_COLORKEY)

        self.button.create_image(self.width//2, self.height//2, image=self.image, tags=('image'))
        self.button.create_text(self.width//2, self.height//2, text=text)

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