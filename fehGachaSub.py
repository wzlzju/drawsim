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
    import numpy as np
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
            if b is not None:
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
            if b is not None:
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

class strategyPanel(object):
    def __init__(self, root, resultVar):
        self.root = root
        self.resultVar = resultVar
        self.selectedItem = None

    def initialization(self, setting=None):
        # constants
        self.result = self.getresult(self.resultVar.get())
        self.buttonsize = (60,60)
        self.w_num = len(COLORS)
        self.buttonConfigs = {
            "size": self.buttonsize,
            "rownum": self.w_num
        }

        # containers
        self.buttonList = []
        self.imgHolder = []

        # configs
        self.config = dict_merge(self.buttonConfigs, {"callbackFunc": self.func, "buttonList": self.buttonList,
                                                    "imageFunc": lambda i,e: "util/"+e, "imgholder": self.imgHolder})

        # widgets
        Label(self.root, text="Wanted:").grid(row=0, column=0, rowspan=1, columnspan=1, padx=5, pady=5, sticky="nsew")
        Label(self.root, text="Unwanted:").grid(row=1, column=0, rowspan=1, columnspan=1, padx=5, pady=5, sticky="nsew")
        self.strategy = Canvas(self.root, bg="white", highlightthickness=0)
        self.strategy.grid(row=0, column=1, rowspan=2, columnspan=2, padx=5, pady=5, sticky="nsew")

        self.updateStrategy()
    
    def getresult(self, resstr):
        res = {
            "wanted": [],
            "unwanted": []
        }
        for c in resstr:
            if c in ['R','B','G','W']:
                flag = "wanted"
            elif c in ['r','b','g','w']:
                flag = "unwanted"
            res[flag].append({
                'r': 'red',
                'b': 'blue',
                'g': 'green',
                'w': 'gray'
            }[c.lower()])
        return res
    
    def moveresult(self, c1, c2):
        # move c1 to position of c2
        # c2 not in COLORS means empty row
        if c2 in COLORS:
            f1 = "wanted" if c1 in self.result["wanted"] else "unwanted"
            f2 = "wanted" if c2 in self.result["wanted"] else "unwanted"
            self.result[f1] = self.result[f1][:self.result[f1].index(c1)]+self.result[f1][self.result[f1].index(c1)+1:]
            self.result[f2] = self.result[f2][:self.result[f2].index(c2)]+[c1]+self.result[f2][self.result[f2].index(c2):]
        else:
            f1 = "wanted" if c1 in self.result["wanted"] else "unwanted"
            f2 = "wanted" if f1=="unwanted" else "unwanted"
            self.result[f1] = self.result[f1][:self.result[f1].index(c1)]+self.result[f1][self.result[f1].index(c1)+1:]
            self.result[f2] = [c1]

    def func(self, tag, index, element, **kwargs):
        if self.selectedItem is None:
            if element in COLORS:
                self.selectedItem = {"index": index, "element": element}
                self.buttonList[index]["relief"] = SUNKEN
        else:
            self.buttonList[self.selectedItem["index"]]["relief"] = RAISED
            if self.selectedItem["element"] == element:
                pass
            else:
                self.moveresult(self.selectedItem["element"], element)
                self.updateStrategy()
                self.setResultVar()
            self.selectedItem = None
    
    def updateStrategy(self):
        for b in self.buttonList:
            if b is not None:
                b.grid_forget()
        self.buttonList.clear()
        self.imgHolder.clear()
        config = dict_merge(self.config, {"imageFunc": lambda i,e: ""})

        if self.result["wanted"]:
            buttonArray(root=self.strategy, elements=self.result["wanted"], tag="wanted", aligned=True, **self.config)
        else:
            buttonArray(root=self.strategy, elements=[""], tag="wanted", aligned=True, **config)
        if self.result["unwanted"]:
            buttonArray(root=self.strategy, elements=self.result["unwanted"], tag="unwanted", begin_index=self.w_num, aligned=True, **self.config)
        else:
            buttonArray(root=self.strategy, elements=[""], tag="unwanted", begin_index=self.w_num, aligned=True, **config)
    
    def setResultVar(self):
        mapping = {"red":'r', "blue":'b', "green":'g', "gray":'w'}
        resStr = "".join([mapping[c].upper() for c in self.result["wanted"]]+[mapping[c].lower() for c in self.result["unwanted"]])
        self.resultVar.set(resStr)


def getimage(holders, label, size=(60, 60)):
    if label:
        imgpath = os.path.join(IMGPATH, label)
        imgpath = addImgExt(imgpath)
        img = Image.open(imgpath)
        img = img.resize(size)
    else:
        img = Image.fromarray(np.zeros((size[0],size[1],4),dtype=np.uint8))
    holders.append(ImageTk.PhotoImage(img))

def buttonArray(elements=None, textFunc=None, imageFunc=None, begin_index=0, buttonList=None, aligned=False, **kwargs):
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
            if aligned:
                for j in range(i-len(buttonList)):
                    buttonList.append(None)
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



