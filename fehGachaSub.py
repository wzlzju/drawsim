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


class VerticalScrolledFrame(ttk.Frame):
    """
    https://stackoverflow.com/questions/16188420/tkinter-scrollbar-for-frame
    """
    def __init__(self, parent, *args, **kw):
        ttk.Frame.__init__(self, parent, *args, **kw)

        # Create a canvas object and a vertical scrollbar for scrolling it.
        vscrollbar = ttk.Scrollbar(self, orient=VERTICAL)
        vscrollbar.pack(fill=Y, side=RIGHT, expand=FALSE)
        self.canvas = canvas = Canvas(self, *args, bd=0, highlightthickness=0, yscrollcommand=vscrollbar.set, **kw)
        canvas.pack(side=LEFT, fill=BOTH, expand=TRUE)
        vscrollbar.config(command=canvas.yview)

        self.resetViews()

        # Create a frame inside the canvas which will be scrolled with it.
        self.interior = interior = ttk.Frame(canvas)
        interior_id = canvas.create_window(0, 0, window=interior, anchor=NW)

        # Track changes to the canvas and frame width and sync them,
        # also updating the scrollbar.
        def _configure_interior(event):
            # Update the scrollbars to match the size of the inner frame.
            size = (interior.winfo_reqwidth(), interior.winfo_reqheight())
            canvas.config(scrollregion="0 0 %s %s" % size)
            if interior.winfo_reqwidth() != canvas.winfo_width():
                # Update the canvas's width to fit the inner frame.
                canvas.config(width=interior.winfo_reqwidth())
        interior.bind('<Configure>', _configure_interior)

        def _configure_canvas(event):
            if interior.winfo_reqwidth() != canvas.winfo_width():
                # Update the inner frame's width to fill the canvas.
                canvas.itemconfigure(interior_id, width=canvas.winfo_width())
        canvas.bind('<Configure>', _configure_canvas)

        def _on_mousewheel(event):
            delta = int(event.delta/120) if os.name=="nt" else event.delta
            canvas.yview_scroll(-1*delta, "units")
        canvas.bind_all("<MouseWheel>", _on_mousewheel)
    
    def resetViews(self):
        self.canvas.xview_moveto(0)
        self.canvas.yview_moveto(0)


class charaPanel(object):
    def __init__(self, root, resultVar, charasCol=8, charasRow=14, buttonsize=(30,30)):
        self.root = root
        self.resultVar = resultVar if type(resultVar) is StringVar else None
        self.resultVars = resultVar if type(resultVar) is dict else None
        self.charasCol = charasCol
        self.charasRow = charasRow
        self.buttonsize = buttonsize
        self.charasWidth = (self.buttonsize[0]+10)*self.charasCol
        self.charasHeight = (self.buttonsize[1]+10)*self.charasRow

    def initialization(self, setting=None):
        # constants
        self.result = self.getresult()
        self.options = {_:set() for _ in OPTIONS}
        self.smallButtonConfigs = {
            "size": self.buttonsize,
            "rownum": self.charasCol
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
        # textFilterConfig = dict_merge(filterConfig, {"textFunc": lambda i,e: str(e)})
        versionFilterConfig = dict_merge(filterConfig, {"imageFunc": lambda i,e: "util/%d"%e, "imgholder": self.filterImgHolder})
        gameFilterConfig = dict_merge(filterConfig, {"imageFunc": lambda i,e: "util/game%d"%e, "imgholder": self.filterImgHolder})
        
        # widgets
        self.results = Canvas(self.root, highlightthickness=0)
        self.results.grid(row=0, column=0, rowspan=2, columnspan=4, padx=5, pady=5, sticky="nsew")
        
        self.filters = Canvas(self.root, highlightthickness=0)
        self.filters.grid(row=2, column=0, rowspan=5, columnspan=4, padx=5, pady=5, sticky="nsew")
        buttonArray(root=self.filters, elements=OPTIONS["color"], tag="color", **imgFilterConfig)
        buttonArray(root=self.filters, elements=OPTIONS["move"], tag="move", begin_index=len(self.filterButtonList), **imgFilterConfig)
        buttonArray(root=self.filters, elements=OPTIONS["weapon"], tag="weapon", begin_index=len(self.filterButtonList), **imgFilterConfig)
        buttonArray(root=self.filters, elements=OPTIONS["version"], tag="version", begin_index=len(self.filterButtonList), **versionFilterConfig)
        buttonArray(root=self.filters, elements=OPTIONS["game"], tag="game", begin_index=len(self.filterButtonList), **gameFilterConfig)

        self.charasframe = VerticalScrolledFrame(self.root, height=self.charasHeight)
        self.charasframe.grid(row=7, column=0, rowspan=4, columnspan=4, padx=5, pady=5, sticky="nsew")
        self.charascanvas = Canvas(self.root, highlightthickness=0)
        self.charas = self.charasframe.interior
        self.charas.scroll = True

        # settings
        if setting:
            for option_type in OPTIONS:
                if setting.get(option_type, None):
                    self.options[option_type] = set(setting[option_type])
        self.updateFilters()
        self.updateCharas()
    
    def getresult(self):
        if self.resultVar is not None:
            return self._getresultfromstring(self.resultVar.get())
        else:
            return functools.reduce(lambda x,y:x+y, [self._getresultfromstring(var.get()) for var in self.resultVars.values()])
    
    def _getresultfromstring(self, resstr):
        return resstr.split(',') if len(resstr)>0 else []
    
    def setresult(self, reslist):
        if self.resultVar is not None:
            self.resultVar.set(self._resl2str(reslist))
        else:
            color2names = {
                "red": [],
                "blue": [],
                "green": [],
                "gray": []
            }
            list(map(lambda name:color2names[name2color[name]].append(name), reslist))
            list(map(lambda color:self.resultVars[color].set(self._resl2str(color2names[color])), self.resultVars.keys()))
    
    def _resl2str(self, reslist):
        return ','.join(reslist)
    
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
            if len(self.options['game']) > 0:
                if type(hero["game"]) is int and hero["game"] not in self.options['game']:
                    flag = False
                elif type(hero["game"]) is str and \
                    functools.reduce(lambda x,y:x and y, [int(g) not in self.options['game'] for g in hero["game"].split(',')]):
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
        if self.charas.scroll and len(charas) <= self.charasCol*self.charasRow:
            self.charasframe.grid_forget()
            self.charascanvas.grid(row=7, column=0, rowspan=4, columnspan=4, padx=5, pady=5, sticky="nsew")
            self.charas = self.charascanvas
            self.charas.scroll = False
        elif not self.charas.scroll and len(charas) > self.charasCol*self.charasRow:
            self.charascanvas.grid_forget()
            self.charasframe.grid(row=7, column=0, rowspan=4, columnspan=4, padx=5, pady=5, sticky="nsew")
            self.charas = self.charasframe.interior
            self.charas.scroll = True
        buttonArray(root=self.charas, elements=charas, tag="chara", **config)
        
        self.charasframe.resetViews()
    
    def charaFunc(self, tag, index, element, **kwargs):
        self.result.append(element["name"])
        self.setresult(self.result)
        # self.resultVar.set(','.join(self.result))
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
        self.setresult(self.result)
        # self.resultVar.set(','.join(self.result))
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
        try:
            imgpath = os.path.join(IMGPATH, label)
            imgpath = addImgExt(imgpath)
            img = Image.open(imgpath)
            img = img.resize(size)
        except:     # no image file
            img = Image.fromarray(np.zeros((size[0],size[1],4),dtype=np.uint8))
            draw = ImageDraw.Draw(img)
            font = ImageFont.truetype("arial.ttf", 16)
            draw.text((int(size[0]*0.3), int(size[1]*0.25)), label.split('/')[-1], (0,0,0), font=font)
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
        # button = Button(root, text=text, command=lambda t=tag,i=index,e=element: callbackFunc(t,i,e))
        getimage(imgholder, text, size)
        button = Button(root, image=imgholder[-1], command=lambda t=tag,i=index,e=element: callbackFunc(t,i,e))
    elif image is not None:
        getimage(imgholder, image, size)
        button = Button(root, image=imgholder[-1], command=lambda t=tag,i=index,e=element: callbackFunc(t,i,e))
    button.grid(row=index//rownum, column=index%rownum, rowspan=1, columnspan=1, padx=1, pady=1, sticky="nsew")
    return button

class stopPanel(object):
    def __init__(self, root, resultVar, up=None, debug_print=print):
        self.root = root
        self.resultVar = resultVar
        self.parser = stopParser()
        self.up = up if up else []
        self.debug_print = debug_print

    def initialization(self, setting=None):
        self.tree = self.parser.reform(self.parser.parse(self.resultVar.get()))
        self.canvas = Canvas(self.root, highlightthickness=0)
        self.canvas.grid(row=0, column=0)
        drawTree(self.canvas, self.tree, 0, 0, callback=self.responseActionOnTree, index=[], cmpop_values=self.up+[h["name"] for h in data["heroes"]])
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
            if cnode["op"] in PRESETTINGOPS and len(cnode["obj"])!=2:
                cnode["obj"] = ["red", 11]
            if cnode["op"] in CMPOPS and len(cnode["obj"])!=2:
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
                cnode["op"] = "and"
                cnode["obj"] = []
            else:
                pnode["obj"] = pnode["obj"][:cindex] + pnode["obj"][cindex+1:]
        
        if action in ["select_op", "add_child", "remove_this"]:
            self.canvas.grid_forget()
            self.canvas = Canvas(self.root, highlightthickness=0)
            self.canvas.grid(row=0, column=0)
            drawTree(self.canvas, self.tree, 0, 0, callback=self.responseActionOnTree, index=[])
    
    def confirmStop(self):
        try:
            self.resultVar.set(self.parser.dump(self.parser.reform_back(self.tree)))
        except Exception as e:
            self.debug_print(e)

    
def drawTree(root, tree, crow, cdepth, callback, index, **kwargs):
    LogExp_RowWidget(root, tree, crow, cdepth, callback, index, **kwargs)
    drawnrownum = 1

    if type(tree) is not str and type(tree) is not int:
        op = tree["op"]
        obj = tree["obj"]
        if op in LOGICOPS:
            for i, node in enumerate(obj):
                drawnrownum += drawTree(root, node, crow+drawnrownum, cdepth+1, callback=callback, index=index+[i], **kwargs)
    return drawnrownum
        

def LogExp_RowWidget(root, node, rownum, depth, callback, nodeindex, **kwargs):
    row = Canvas(root, highlightthickness=0)
    row.grid(row=rownum, column=1, rowspan=1, columnspan=1, padx=5, pady=5, sticky="nsew")

    indent = Label(row, image=PhotoImage(width=1, height=1),height=24,width=depth*24, padx=0,pady=0)
    # indent.grid(row=0, column=0, rowspan=1, columnspan=1, sticky="w")
    indent.pack(side=LEFT)
    # str/int as a leaf node
    if type(node) in [str, int, bool]:
        # Label(row, text=str(node)).grid(row=0, column=1, rowspan=1, columnspan=1, sticky="w")
        Label(row, text=str(node)).pack(side=LEFT)
        createTextButton(row, "-", 0, 2, callback=callback, side=RIGHT, action="remove_this", nodeindex=nodeindex)
        return
    op = node["op"]
    obj = node["obj"]
    if op in LOGICOPS:
        createCombobox(row, list(TX2OP.keys()), 0, 1, init=OP2TX[op], callback=callback, action="select_op", nodeindex=nodeindex)
        createTextButton(row, "-", 0, 3, callback=callback, side=RIGHT, action="remove_this", nodeindex=nodeindex)
        createTextButton(row, "+", 0, 2, callback=callback, side=RIGHT, action="add_child", nodeindex=nodeindex)
    elif op in PRESETTINGOPS:
        createCombobox(row, list(TX2OP.keys()), 0, 1, init=OP2TX[op], callback=callback, action="select_op", nodeindex=nodeindex)
        createCombobox(row, COLORS, 0, 2, init=obj[0], callback=callback, action="select_obj1", nodeindex=nodeindex)
        createInputbox(row, 0, 3, init=str(obj[1]), callback=callback, action="input_obj2", nodeindex=nodeindex)
        createTextButton(row, "-", 0, 4, callback=callback, side=RIGHT, action="remove_this", nodeindex=nodeindex)
    elif op in CMPOPS:
        createCombobox(row, kwargs.get("cmpop_values", [h["name"] for h in data["heroes"]]), 0, 1, init=obj[0], callback=callback, action="select_obj1", nodeindex=nodeindex)
        createCombobox(row, list(TX2OP.keys()), 0, 2, init=OP2TX[op], callback=callback, action="select_op", nodeindex=nodeindex)
        createInputbox(row, 0, 3, init=str(obj[1]), callback=callback, action="input_obj2", nodeindex=nodeindex)
        createTextButton(row, "-", 0, 4, callback=callback, side=RIGHT, action="remove_this", nodeindex=nodeindex)
    # indent.configure(bg=OPCOLORS_BG.get(op, OPCOLORS_BG["default"]))
    row.configure(bg=OPCOLORS_BG.get(op, OPCOLORS_BG["default"]))

def createCombobox(root, values, r, c, init, callback, width=10, padx=2, pady=2, sticky='w', side=LEFT, **kwargs):
    box = ttk.Combobox(root, values=values, width=width)
    # box.grid(row=r, column=c, padx=padx, pady=pady, sticky=sticky)
    box.pack(side=side)
    box.set(init)
    box.__dict__ = dict_merge(box.__dict__, kwargs)
    box.bind("<<ComboboxSelected>>", callback)

def createInputbox(root, r, c, init, callback, width=10, padx=2, pady=2, sticky='w', side=LEFT, **kwargs):
    box = Entry(root, width=width)
    # box.grid(row=r, column=c, padx=padx, pady=pady, sticky=sticky)
    box.pack(side=side)
    setEntry(box, init)
    box.__dict__ = dict_merge(box.__dict__, kwargs)
    box.bind("<KeyRelease>", callback)

def createTextButton(root, text, r, c, callback, height=16, width=16, padx=2, pady=2, sticky='w', side=LEFT, **kwargs):
    pixel = PhotoImage(width=1, height=1)
    button = Button(root, text=text, image=pixel, compound="center", padx=0, pady=0, height=height, width=width)
    # button.grid(row=r, column=c, padx=padx, pady=pady, sticky=sticky)
    button.pack(side=side)
    button.__dict__ = dict_merge(button.__dict__, kwargs)
    button.bind("<Button-1>", callback)

def setEntry(entry, text):
    entry.delete(0,END)
    entry.insert(0, text)


        


