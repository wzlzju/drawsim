from tkinter import *
from tkinter import ttk
from tkinter.constants import DISABLED, NORMAL, ACTIVE
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
import random, math, re, os, collections, copy, functools

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
        # constants
        self.result = self.getresult(self.resultVar.get())
        self.options = {_:set() for _ in OPTIONS}
        self.buttonsize = (30,30)
        self.w_num = len(COLORS)+len(MOVES)
        self.smallButtonConfigs = {
            "size": self.buttonsize,
            "rownum": self.w_num
        }

        # containers
        self.filterButtonList = []
        self.filterImgHolder = []
        self.charaButtonList = []
        self.charaImgHolder = []
        self.resultButtonList = []
        self.resultImgHolder = []

        # configs
        filterConfig = dict_merge(self.smallButtonConfigs, {"callbackFunc": self.filterFunc, "buttonList": self.filterButtonList})
        imgFilterConfig = dict_merge(filterConfig, {"imageFunc": lambda i,e: "util/"+e, "imgholder": self.filterImgHolder})
        textFilterConfig = dict_merge(filterConfig, {"textFunc": lambda i,e: str(e)})

        # widgets
        self.results = Canvas(self.root, bg="white", highlightthickness=0)
        self.results.grid(row=0, column=0, rowspan=2, columnspan=4, padx=5, pady=5, sticky="nsew")
        
        self.filters = Canvas(self.root, bg="white", highlightthickness=0)
        self.filters.grid(row=2, column=0, rowspan=5, columnspan=4, padx=5, pady=5, sticky="nsew")
        buttonArray(root=self.filters, elements=OPTIONS["color"], tag="color", **imgFilterConfig)
        buttonArray(root=self.filters, elements=OPTIONS["move"], tag="move", begin_index=len(self.filterButtonList), **imgFilterConfig)
        buttonArray(root=self.filters, elements=OPTIONS["weapon"], tag="weapon", begin_index=len(self.filterButtonList), **imgFilterConfig)
        buttonArray(root=self.filters, elements=OPTIONS["version"], tag="version", begin_index=len(self.filterButtonList), **textFilterConfig)

        self.charas = Canvas(self.root, bg="white", highlightthickness=0)
        self.charas.grid(row=7, column=0, rowspan=4, columnspan=4, padx=5, pady=5, sticky="nsew")

        # settings
        if setting:
            for option_type in OPTIONS:
                if setting.get(option_type, None):
                    self.options[option_type] = set(setting[option_type])
        self.updateFilters()
        self.updateCharas()
    
    def getresult(self, resstr):
        return resstr.split(',') if len(resstr)>0 else []
    
    def filterFunc(self, tag, index, element, **kwargs):
        if self.filterButtonList[index]["relief"] == SUNKEN:
            self.options[tag].remove(element)
            self.filterButtonList[index]["relief"] = RAISED
        elif self.filterButtonList[index]["relief"] == RAISED:
            self.options[tag].add(element)
            self.filterButtonList[index]["relief"] = SUNKEN
        # print(self.options)
        self.updateCharas()
    
    def updateFilters(self):
        optionNames = functools.reduce(lambda a,b: a+b, OPTIONS.values())
        name2type = dict(zip(functools.reduce(lambda a,b:a+b,OPTIONS.values()), 
                            functools.reduce(lambda a,b:a+b,[[_ for __ in range(len(OPTIONS[_]))] for _ in OPTIONS])))
        for optionName, filterButton in zip(optionNames, self.filterButtonList):
            if optionName in self.options[name2type[optionName]]:
                filterButton["relief"] = SUNKEN
            else:
                filterButton["relief"] = RAISED
    
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
        for b in self.charaButtonList:
            b.grid_forget()
        self.charaButtonList.clear()
        self.charaImgHolder.clear()
        config = dict_merge(self.smallButtonConfigs, {"callbackFunc": self.charaFunc, "buttonList": self.charaButtonList, 
                                                        "imageFunc": lambda i,e: "chara/"+e["name"], "imgholder": self.charaImgHolder})
        buttonArray(root=self.charas, elements=charas, tag="chara", **config)
    
    def charaFunc(self, tag, index, element, **kwargs):
        self.result.append(element["name"])
        self.resultVar.set(','.join(self.result))
        self.updateResult()

    def updateResult(self):
        for b in self.resultButtonList:
            b.grid_forget()
        self.resultButtonList.clear()
        self.resultImgHolder.clear()
        config = dict_merge(self.smallButtonConfigs, {"callbackFunc": self.resultFunc, "buttonList": self.resultButtonList, 
                                                        "imageFunc": lambda i,e: "chara/"+e, "imgholder": self.resultImgHolder})
        buttonArray(root=self.results, elements=self.result, tag="chara", **config)
    
    def resultFunc(self, tag, index, element, **kwargs):
        del self.result[index]
        self.resultVar.set(','.join(self.result))
        self.updateResult()

def getimage(holders, label, size=(60, 60)):
        imgpath = os.path.join(IMGPATH, label)
        imgpath = addImgExt(imgpath)
        img = Image.open(imgpath)
        img = img.resize(size)
        holders.append(ImageTk.PhotoImage(img))

def buttonArray(elements=None, textFunc=None, imageFunc=None, begin_index=0, buttonList=None, **kwargs):
    if not elements:
        return
    if textFunc is None and imageFunc is None:
        print("Error: No text and no image Func given in buttonArray of", elements)
    if NOPIL and textFunc is None:
        textFunc = lambda i,e: str(e)
    for ii, e in enumerate(elements):
        i = ii+begin_index
        if textFunc is not None:
            text = textFunc(i, e)
            button = buttonEntry(index=i, element=e, text=text, **kwargs)
        elif imageFunc is not None:
            image = imageFunc(i, e)
            button = buttonEntry(index=i, element=e, image=image, **kwargs)
        if buttonList is not None:
            buttonList.append(button)

def buttonEntry(root=None, tag="", index=0, element=None, callbackFunc=None, text=None, image=None, imgholder=None, size=(60,60), rownum=8, **kwargs):
    if root is None or element is None or callbackFunc is None:
        print("Error: No text and no image given in buttonEntry of", root, element, "False calling.")
    if text is None and image is None:
        print("Error: No text and no image given in buttonEntry of", root, element)
    if NOPIL and text is None:
        text = str(image)
    if text is not None:
        button = Button(root, text=text, command=lambda t=tag,i=index,e=element: callbackFunc(t,i,e))
    elif image is not None:
        getimage(imgholder, image, size)
        button = Button(root, image=imgholder[-1], command=lambda t=tag,i=index,e=element: callbackFunc(t,i,e))
    button.grid(row=index//rownum, column=index%rownum, rowspan=1, columnspan=1, padx=1, pady=1, sticky="nsew")
    return button

# def buttonArray(root, elements, callbackFunc, textFunc=None, imageFunc=None, imgholder=None, tag="", begin_index=0, buttonList=None, size=(60,60), rownum=8):
#     for ii, e in enumerate(elements):
#         i = ii+begin_index
#         if textFunc is not None:
#             text = textFunc(i, e)
#             button = buttonEntry(root, tag, i, e, callbackFunc, text=text, size=size, rownum=rownum)
#         elif imageFunc is not None:
#             image = imageFunc(i, e)
#             button = buttonEntry(root, tag, i, e, callbackFunc, image=image, imgholder=imgholder, size=size, rownum=rownum)
#         if buttonList is not None:
#             buttonList.append(button)

# def buttonEntry(root, tag, index, element, callbackFunc, text=None, image=None, imgholder=None, size=(60,60), rownum=8):
#     if text is None and image is None:
#         print("Error: No text and no image given in buttonEntry of", root)
#     if NOPIL and text is None:
#         text = str(image)
#     if text is not None:
#         button = Button(root, text=text, command=lambda t=tag,i=index,e=element: callbackFunc(t,i,e))
#     elif image is not None:
#         getimage(imgholder, image, size)
#         button = Button(root, image=imgholder[-1], command=lambda t=tag,i=index,e=element: callbackFunc(t,i,e))
#     button.grid(row=index//rownum, column=index%rownum, rowspan=1, columnspan=1, padx=1, pady=1, sticky="nsew")
#     return button



