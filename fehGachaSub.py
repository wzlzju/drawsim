from tkinter import *
from tkinter import ttk
from tkinter.constants import DISABLED, NORMAL, ACTIVE
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
import random, math, re, os, collections, copy

import fehGacha as gacha
from const import *
from util import *
try:
    from PIL import Image, ImageTk
    NOPIL = False
except:
    NOPIL = True
try:
    # from fehdata import data
    from tmpdata import data
    NODATA = False
except:
    NODATA = True




class charaPanel(object):
    def __init__(self, root, resultVar):
        self.root = root
        self.resultVar = resultVar

    def initialization(self, setting=None):
        self.result = self.getresult(self.resultVar.get())
        self.options = {
            "color": set(),
            "move": set(),
            "weapon": set(),
            "version": set()
        }

        self.results = Canvas(self.root, bg="white", highlightthickness=0)
        self.results.grid(row=0, column=0, rowspan=2, columnspan=4, padx=5, pady=5, sticky="nsew")
        
        self.buttonList = []
        self.buttonImgHolder = []
        self.buttons = Canvas(self.root, bg="white", highlightthickness=0)
        self.buttons.grid(row=2, column=0, rowspan=5, columnspan=4, padx=5, pady=5, sticky="nsew")
        self.w_num = len(COLORS)+len(MOVES)
        for i, color in enumerate(COLORS):
            self.getimage(self.buttonImgHolder, "util/"+color, (30, 30))
            tags = ("color", color)
            button = Button(self.buttons, image=self.buttonImgHolder[-1], command=lambda i=len(self.buttonList),t=tags: self.buttonFunc(i,t))
            button.grid(row=len(self.buttonList)//self.w_num, column=len(self.buttonList)%self.w_num, rowspan=1, columnspan=1, padx=1, pady=1, sticky="nsew")
            self.buttonList.append(button)
        for i, move in enumerate(MOVES):
            self.getimage(self.buttonImgHolder, "util/"+move, (30, 30))
            tags = ("move", move)
            button = Button(self.buttons, image=self.buttonImgHolder[-1], command=lambda i=len(self.buttonList),t=tags: self.buttonFunc(i,t))
            button.grid(row=len(self.buttonList)//self.w_num, column=len(self.buttonList)%self.w_num, rowspan=1, columnspan=1, padx=1, pady=1, sticky="nsew")
            self.buttonList.append(button)
        for i, weapon in enumerate(WEAPONS):
            self.getimage(self.buttonImgHolder, "util/"+weapon, (30, 30))
            tags = ("weapon", weapon)
            button = Button(self.buttons, image=self.buttonImgHolder[-1], command=lambda i=len(self.buttonList),t=tags: self.buttonFunc(i,t))
            button.grid(row=len(self.buttonList)//self.w_num, column=len(self.buttonList)%self.w_num, rowspan=1, columnspan=1, padx=1, pady=1, sticky="nsew")
            self.buttonList.append(button)
        for i, version in enumerate(VERSIONS):
            tags = ("version", version)
            button = Button(self.buttons, text=str(version), command=lambda i=len(self.buttonList),t=tags: self.buttonFunc(i,t))
            button.grid(row=len(self.buttonList)//self.w_num, column=len(self.buttonList)%self.w_num, rowspan=1, columnspan=1, padx=1, pady=1, sticky="nsew")
            self.buttonList.append(button)

        self.charas = Canvas(self.root, bg="white", highlightthickness=0)
        self.charas.grid(row=7, column=0, rowspan=4, columnspan=4, padx=5, pady=5, sticky="nsew")

        if setting:
            if setting.get("color", None):
                self.options["color"] = set(setting["color"])
            if setting.get("move", None):
                self.options["move"] = set(setting["move"])
            if setting.get("weapon", None):
                self.options["weapon"] = set(setting["weapon"])
            if setting.get("version", None):
                self.options["version"] = set(setting["version"])
        self.updateButtons()
        self.updateCharas()

    def getimage(self, holders, label, size=(60, 60)):
        imgpath = os.path.join(IMGPATH, label)
        imgpath = addImgExt(imgpath)
        img = Image.open(imgpath)
        img = img.resize(size)
        holders.append(ImageTk.PhotoImage(img))
    
    def getresult(self, resstr):
        if len(resstr) == 0:
            return []
        return resstr.split(',')
    
    def buttonFunc(self, index, tags):
        if self.buttonList[index]["relief"] == SUNKEN:
            self.options[tags[0]].remove(tags[1])
            self.buttonList[index]["relief"] = RAISED
        elif self.buttonList[index]["relief"] == RAISED:
            self.options[tags[0]].add(tags[1])
            self.buttonList[index]["relief"] = SUNKEN
        # print(self.options)
        self.updateCharas()
    
    def updateButtons(self):
        for i, color in enumerate(COLORS):
            if color in self.options["color"]:
                self.buttonList[i]["relief"] = SUNKEN
            else:
                self.buttonList[i]["relief"] = RAISED
        for i, move in enumerate(MOVES):
            if move in self.options["move"]:
                self.buttonList[i+len(COLORS)]["relief"] = SUNKEN
            else:
                self.buttonList[i+len(COLORS)]["relief"] = RAISED
        for i, weapon in enumerate(WEAPONS):
            if weapon in self.options["weapon"]:
                self.buttonList[i+len(COLORS)+len(MOVES)]["relief"] = SUNKEN
            else:
                self.buttonList[i+len(COLORS)+len(MOVES)]["relief"] = RAISED
        for i, version in enumerate(VERSIONS):
            if version in self.options["version"]:
                self.buttonList[i+len(COLORS)+len(MOVES)+len(WEAPONS)]["relief"] = SUNKEN
            else:
                self.buttonList[i+len(COLORS)+len(MOVES)+len(WEAPONS)]["relief"] = RAISED
    
    def filtering(self):
        charas = []
        for hero in data["heroes"]:
            flag = True
            if len(self.options['color']) > 0:
                if hero["color"] not in self.options['color']:
                    flag = False
            if len(self.options['move']) > 0:
                if hero["movetype"] not in self.options['move']:
                    flag = False
            if len(self.options['weapon']) > 0:
                if hero["weapontype"] not in self.options['weapon'] and hero["color"]+hero["weapontype"] not in self.options['weapon']:
                    flag = False
            if len(self.options['version']) > 0:
                if hero["version"] == "":
                    flag = False
                elif int(hero["version"].split(',')[0]) not in self.options['version']:
                    flag = False
            if flag:
                charas.append(hero)
        return charas

    def updateCharas(self):
        charas = self.filtering()
        self.charaImgHolder = []
        for i, chara in enumerate(charas):
            self.getimage(self.charaImgHolder, "chara/"+chara["name"], (30, 30))
            tags = ("chara", chara["name"])
            button = Button(self.charas, image=self.charaImgHolder[-1], command=lambda i=i,t=tags: self.charaFunc(i,t))
            button.grid(row=i//(len(COLORS)+len(MOVES)), column=i%(len(COLORS)+len(MOVES)), rowspan=1, columnspan=1, padx=1, pady=1, sticky="nsew")
            # self.buttonList.append(button)
    
    def charaFunc(self, index, tags):
        self.result.append(tags[1])
        self.resultVar.set(','.join(self.result))
        self.updateResult()

    def updateResult(self):
        self.resultImgHolder = []
        for i, res in enumerate(self.result):
            self.getimage(self.resultImgHolder, "chara/"+res, (30, 30))
            tags = ("chara", res)
            button = Button(self.results, image=self.resultImgHolder[-1], command=lambda i=i,t=tags: self.resultFunc(i,t))
            button.grid(row=i//(len(COLORS)+len(MOVES)), column=i%(len(COLORS)+len(MOVES)), rowspan=1, columnspan=1, padx=1, pady=1, sticky="nsew")
            # self.buttonList.append(button)
    
    def resultFunc(self, index, tags):
        del self.result[index]
        self.resultVar.set(','.join(self.result))
        self.updateResult()

        