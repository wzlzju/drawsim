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

class stopPanel(object):
    def __init__(self, root, resultVar):
        self.root = root
        self.resultVar = resultVar
        self.parser = stopParser()

    def initialization(self, setting=None):
        self.tree = self.parser.reform(self.parser.parse(self.resultVar.get()))
        self.canvas = Canvas(self.root, highlightthickness=0)
        self.canvas.grid(row=0, column=0)
        drawTree(self.canvas, self.tree, 0, 0, callback=self.responseActionOnTree, index=[])
        Button(self.root, text="Confirm", command=self.confirmStop).grid(row=1, column=0, sticky="nsew")
    
    def responseActionOnTree(self, event):
        widget = event.widget
        action = widget.action
        nodeindex = widget.nodeindex            
        # locate current node
        cnode = self.tree
        pnode = None
        for i in nodeindex:
            pnode = cnode
            cindex = i
            cnode = pnode["obj"][cindex]

        if action == "select_op":
            cnode["op"] = TX2OP[widget.get()]
            if cnode["op"] in PRESETTINGOPS and len(cnode["obj"])==0:
                cnode["obj"] = ["red", 11]
            if cnode["op"] in CMPOPS and len(cnode["obj"])==0:
                cnode["obj"] = [[h["name"] for h in data["heroes"]][0], 11]
        elif action == "select_obj1":
            cnode["obj"][0] = widget.get()
        elif action == "input_obj2":
            try:
                cnode["obj"][1] = int(widget.get())
            except:
                cnode["obj"][1] = -1
        elif action == "add_child":
            cnode["obj"].append({"op":"and","obj":[]})
        elif action == "remove_this":
            if pnode is None:
                pass
            else:
                pnode["obj"] = pnode["obj"][:cindex] + pnode["obj"][cindex+1:]
        
        self.canvas.grid_forget()
        self.canvas = Canvas(self.root, highlightthickness=0)
        self.canvas.grid(row=0, column=0)
        drawTree(self.canvas, self.tree, 0, 0, callback=self.responseActionOnTree, index=[])
    
    def confirmStop(self):
        self.resultVar.set(self.parser.dump(self.parser.reform_back(self.tree)))

    
def drawTree(root, tree, crow, cdepth, callback, index):
    LogExp_RowWidget(root, tree, crow, cdepth, callback, index)
    drawnrownum = 1

    if type(tree) is not str and type(tree) is not int:
        op = tree["op"]
        obj = tree["obj"]
        if op in LOGICOPS:
            for i, node in enumerate(obj):
                drawnrownum += drawTree(root, node, crow+drawnrownum, cdepth+1, callback=callback, index=index+[i])
    return drawnrownum
        

def LogExp_RowWidget(root, node, rownum, depth, callback, nodeindex):
    row = Canvas(root, highlightthickness=0)
    row.grid(row=rownum, column=1, rowspan=1, columnspan=1, sticky="nsew")

    # indent
    Label(row, text="    "*depth).grid(row=0, column=0, rowspan=1, columnspan=1, sticky="w")
    if type(node) is str or type(node) is int:
        # True
        Label(row, text=str(node)).grid(row=0, column=1, rowspan=1, columnspan=1, sticky="w")
        # -
        createTextButton(row, "-", 0, 2, callback=callback, action="remove_this", nodeindex=nodeindex)
        return
    op = node["op"]
    obj = node["obj"]
    # Label(row, text=op if op in ["and", "or", "not"] else str(node)).grid(row=0, column=1, rowspan=1, columnspan=1, sticky="nsew")
    if op in LOGICOPS:
        # All
        createCombobox(row, list(TX2OP.keys()), 0, 1, init=OP2TX[op], callback=callback, action="select_op", nodeindex=nodeindex)
        # +
        createTextButton(row, "+", 0, 2, callback=callback, action="add_child", nodeindex=nodeindex)
        # -
        createTextButton(row, "-", 0, 3, callback=callback, padx=0, action="remove_this", nodeindex=nodeindex)
    elif op in PRESETTINGOPS:
        # All
        createCombobox(row, list(TX2OP.keys()), 0, 1, init=OP2TX[op], callback=callback, action="select_op", nodeindex=nodeindex)
        # red
        createCombobox(row, COLORS, 0, 2, init=obj[0], callback=callback, action="select_obj1", nodeindex=nodeindex)
        # 11
        createInputbox(row, 0, 3, init=str(obj[1]), callback=callback, action="input_obj2", nodeindex=nodeindex)
        # -
        createTextButton(row, "-", 0, 4, callback=callback, action="remove_this", nodeindex=nodeindex)
    elif op in CMPOPS:
        # name
        createCombobox(row, [h["name"] for h in data["heroes"]], 0, 1, init=obj[0], callback=callback, action="select_obj1", nodeindex=nodeindex)
        # >=
        createCombobox(row, list(TX2OP.keys()), 0, 2, init=OP2TX[op], callback=callback, action="select_op", nodeindex=nodeindex)
        # 11
        createInputbox(row, 0, 3, init=str(obj[1]), callback=callback, action="input_obj2", nodeindex=nodeindex)
        # -
        createTextButton(row, "-", 0, 4, callback=callback, action="remove_this", nodeindex=nodeindex)

def createCombobox(root, values, r, c, init, callback, width=10, padx=0, pady=0, sticky='w', **kwargs):
    box = ttk.Combobox(root, values=values, width=width)
    box.grid(row=r, column=c, padx=padx, pady=pady, sticky=sticky)
    box.set(init)
    box.__dict__ = dict_merge(box.__dict__, kwargs)
    box.bind("<<ComboboxSelected>>", callback)

def createInputbox(root, r, c, init, callback, width=10, padx=0, pady=0, sticky='w', **kwargs):
    box = Entry(root, width=width)
    box.grid(row=r, column=c, padx=padx, pady=pady, sticky=sticky)
    setEntry(box, init)
    box.__dict__ = dict_merge(box.__dict__, kwargs)
    box.bind("<KeyRelease>", callback)

def createTextButton(root, text, r, c, callback, padx=4, pady=0, sticky='w', **kwargs):
    button = Button(root, text=text)
    button.grid(row=r, column=c, padx=padx, pady=pady, sticky=sticky)
    button.__dict__ = dict_merge(button.__dict__, kwargs)
    button.bind("<Button-1>", callback)

def setEntry(entry, text):
    entry.delete(0,END)
    entry.insert(0, text)

# def LogExp_RowWidget(root, node, rownum, depth, callbacks, nodeindex):
#     row = Canvas(root, highlightthickness=0)
#     row.grid(row=rownum, column=1, rowspan=1, columnspan=1, sticky="nsew")

#     op = node["op"]
#     obj = node["obj"]
#     # if depth > 0:
#     Label(row, text="    "*depth).grid(row=0, column=0, rowspan=1, columnspan=1, sticky="w")
#     # Label(row, text=op if op in ["and", "or", "not"] else str(node)).grid(row=0, column=1, rowspan=1, columnspan=1, sticky="nsew")
#     if op in LOGICOPS:
#         # All
#         modeselectbox = ttk.Combobox(row, values=list(TX2OP.keys()), width=10)
#         modeselectbox.nodeindex = nodeindex
#         modeselectbox.grid(row=0, column=1, sticky="w")
#         modeselectbox.set(OP2TX[op])
#         modeselectbox.bind("<<ComboboxSelected>>", callbacks["select_op"])
#         # +
#         addbutton = Button(row, text="+", command=lambda nodeindex=nodeindex: callbacks["add_child"](nodeindex))
#         addbutton.grid(row=0, column=2, rowspan=1, columnspan=1, padx=4, sticky="w")
#         # -
#         removebutton = Button(row, text="-", command=lambda nodeindex=nodeindex: callbacks["remove_this"](nodeindex))
#         removebutton.grid(row=0, column=3, rowspan=1, columnspan=1, padx=1, sticky="w")
#     elif op in PRESETTINGOPS:
#         # All
#         modeselectbox = ttk.Combobox(row, values=list(TX2OP.keys()), width=10)
#         modeselectbox.nodeindex = nodeindex
#         modeselectbox.grid(row=0, column=1, sticky="w")
#         modeselectbox.set(OP2TX[op])
#         modeselectbox.bind("<<ComboboxSelected>>", callbacks["select_op"])
#         # red
#         colorselectbox = ttk.Combobox(row, values=COLORS, width=10)
#         colorselectbox.nodeindex = nodeindex
#         colorselectbox.grid(row=0, column=2, sticky="w")
#         colorselectbox.set(obj[0])
#         colorselectbox.bind("<<ComboboxSelected>>", callbacks["select_obj1"])
#         # 11
#         numinputbox = Entry(row, width=10)
#         numinputbox.nodeindex = nodeindex
#         numinputbox.grid(row=0, column=3, sticky="w")
#         numinputbox.bind("<KeyRelease>", callbacks["input_obj2"])
#         # -
#         removebutton = Button(row, text="-", command=lambda nodeindex=nodeindex: callbacks["remove_this"](nodeindex))
#         removebutton.grid(row=0, column=4, rowspan=1, columnspan=1, padx=1, sticky="w")
#     elif op in CMPOPS:
#         # name
#         nameselectbox = ttk.Combobox(row, values=[h["name"] for h in data["heroes"]], width=10)
#         nameselectbox.nodeindex = nodeindex
#         nameselectbox.grid(row=0, column=1, sticky="w")
#         nameselectbox.set(obj[0])
#         nameselectbox.bind("<<ComboboxSelected>>", callbacks["select_obj1"])
#         # >=
#         cmpselectbox = ttk.Combobox(row, values=list(TX2OP.keys()), width=10)
#         cmpselectbox.nodeindex = nodeindex
#         cmpselectbox.grid(row=0, column=2, sticky="w")
#         cmpselectbox.set(OP2TX[op])
#         cmpselectbox.bind("<<ComboboxSelected>>", callbacks["select_op"])
#         # 11
#         numinputbox = Entry(row, width=10)
#         numinputbox.nodeindex = nodeindex
#         numinputbox.grid(row=0, column=3, sticky="w")
#         numinputbox.bind("<KeyRelease>", callbacks["input_obj2"])
#         # -
#         removebutton = Button(row, text="-", command=lambda nodeindex=nodeindex: callbacks["remove_this"](nodeindex))
#         removebutton.grid(row=0, column=4, rowspan=1, columnspan=1, padx=1, sticky="w")




        


