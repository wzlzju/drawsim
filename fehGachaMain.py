from tkinter import *
from tkinter import ttk
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
import random, math, re, os, collections, copy, time
import threading

from fehGachaSub import *
import fehGacha as gacha
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

from const import *
from util import *


class Application(Frame):
    def __init__(self, master=None):
        super().__init__(master)
        self.master = master
        self.pack()

        self.width = 300
        self.height = 370

        self.mode = IntVar(self, 0)
        self.up = {
            '5u':{
                'red': StringVar(self, "Robin(M) (Brave)"),
                'blue': StringVar(self, "Gullveig (Brave)"),
                'green': StringVar(self, "Soren (Brave)"),
                'gray': StringVar(self, "Corrin(F) (Brave)")
            },
            '4u':{
                'red': StringVar(self, ""),
                'blue': StringVar(self, ""),
                'green': StringVar(self, ""),
                'gray': StringVar(self, "")
            }
        }
        self.cheatmode = BooleanVar(self, False)
        self.fullexpmode = BooleanVar(self, FULLSTOPFUNC)
        
        self.ballParas = {
            "cx": 150,
            "cy": 150,
            "cr": 100,
            "r": 75
        }

        self.balls = []
        for i in range(5):
            x0 = self.ballParas['cx']-self.ballParas['cr']*math.sin(math.pi*2*i/5)
            y0 = self.ballParas['cy']-self.ballParas['cr']*math.cos(math.pi*2*i/5)
            r = self.ballParas['r']/2
            self.balls.append((x0-r, y0-r, x0+r, y0+r))

        self.strategyStr = StringVar(self, "Wbgr")
        self.stopStr = StringVar(self, "Corrin(F) (Brave) 9")
        # self.stopStr = StringVar(self, "[all gray 11] or (Corrin(F) (Brave) >= 10 and Corrin(F) (Brave) >= 11 or Corrin(F) (Brave) >= 9)")
        self.simu_num = StringVar(self, "10000")
        self.hist_bins = StringVar(self, "20")

        if NODATA:
            self.data = {"heroes":[]}
        else:
            self.data = copy.deepcopy(data)
        self.processData(self.data)

        self.initialize()
        self.createWidget()
        self.inputConfirm()

    def processData(self, data):
        data['id2hero'] = {hero['hero_id']:hero for hero in data["heroes"]}
        data['name2hero'] = {hero['name']:hero for hero in data["heroes"]}
        data['hero_ids'] = set([hero['hero_id'] for hero in data["heroes"]])
        data['names'] = set([hero['name'] for hero in data["heroes"]])

    def initialize(self):
        probs, charas = self.parseUserInput(self.up, self.mode)
        self.tmpdata = {'heroes':[]}
        self.tmpdata['heroes'] = [{
                                    'hero_id':-(idx+1), 
                                    'name':chara['name'], 
                                    'color':chara['color'], 
                                    'minrarity':5
                                } for idx, chara in enumerate(charas['5u']) if chara['name'] not in self.data['names']]
        for idx, chara in enumerate(charas['4u']):
            if chara['name'] in self.data['names']:
                continue
            if chara['name'] not in set([c['name'] for c in self.tmpdata['heroes']]):
                self.tmpdata['heroes'].append({
                                                'hero_id':-(idx+1+len(charas['5u'])), 
                                                'name':chara['name'], 
                                                'color':chara['color'],
                                                'minrarity': 4
                                            })
            else:
                self.tmpdata['heroes'][[c['name'] for c in self.tmpdata['heroes']].index(chara['name'])]['minrarity'] = 4
        self.processData(self.tmpdata)

        self.gacha = gacha.gacha(probs=probs,
                            charas=charas,
                            mode=self.mode)
        self.statistics = {
            '5u': [],
            '5': [],
            '4u': [],
            '4to5': [],
            's4to5': [],
            '34': []
        }
        self.orbs = 0
        self.simu_orbres = None

        self.round = self.gacha.rollARound()
        self.colorList = [c['color'] for c in self.round]

        self.simulationObj = gacha.drawsimulation(
                                gacha=gacha.gacha(
                                    probs=probs,
                                    charas=charas,
                                    mode=self.mode
                                ),
                                strategy=self.simu_parseStrategy if not self.cheatmode.get() else self.simu_parseStrategyCheat,
                                terminate=self.simu_parseStop,
                                app = self
                            )
        self.parser = stopParser()
        
        self.ballImgHolder = [None]*5
        self.charaImgHolder = [None]*5
        self.charaBgHolder = [None]*5
        self.charaBorderHolder = [None]*5

        self.is_simulating = False
    
    def createWidget(self):
        self.inputPanel = Canvas(self, highlightthickness=0)
        self.inputPanel.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")

        self.upInput = Canvas(self.inputPanel, highlightthickness=0)
        self.upInput.grid(row=0, column=0, padx=5, pady=5, sticky="w")
        rowId = 0
        for pup in ['5u', '4u']:
            for color in COLORS:
                upInput = Canvas(self.upInput, highlightthickness=0)
                upInput.grid(row=rowId,column=0, padx=5, pady=5, sticky="w")
                label=Label(upInput, text="%s %s: " % ({'5u':"5* Up", '4u':"4* Up"}[pup], color))
                label.grid(row=0, column=0, padx=5, pady=5, sticky="w")
                entry=Entry(upInput, textvariable=self.up[pup][color])
                entry.grid(row=0, column=1, padx=5, pady=5, sticky="w")
                button=Button(upInput, text="...", command=lambda c=color,textVar=self.up[pup][color]:self.selectChara(c,textVar))
                button.grid(row=0, column=2, padx=5, pady=5, sticky="w")
                rowId += 1
        
        self.modeInput = Canvas(self.inputPanel, highlightthickness=0)
        self.modeInput.grid(row=1, column=0, padx=5, pady=5, sticky="w")
        label=Label(self.modeInput, text="Gacha type:")
        label.grid(row=0, column=0)
        self.modeselectbox = ttk.Combobox(self.modeInput, values=MODES)
        self.modeselectbox.grid(row=0, column=1, padx=5, pady=5, sticky="w")
        self.modeselectbox.set(MODES[0])
        self.modeselectbox.bind("<<ComboboxSelected>>", self.selectMode)
        # for i, mode in enumerate(MODES):
        #     radio=Radiobutton(self.modeInput, text=mode, value=i, variable=self.mode)
        #     radio.grid(row=i+1, column=0, padx=5, pady=5, sticky="w")
        Checkbutton(self.inputPanel, highlightthickness=0, text="cheating mode", variable=self.cheatmode, onvalue=True, offvalue=False, 
            command=self.update_CHEAT).grid(row=2, column=0, padx=5, pady=5, sticky="w")
        Button(self.inputPanel, text='confirm',width=8,command=self.inputConfirm).grid(row=3, column=0, padx=5, pady=5)
        
        

        self.drawPanel = Canvas(self, highlightthickness=0)
        self.drawPanel.grid(row=0, column=1, padx=10, pady=10, sticky="nsew")

        self.canvas = Canvas(self.drawPanel, width=self.width, height=self.height, bg="white", highlightthickness=0)
        self.canvas.grid(row=0, column=0, rowspan=4, columnspan=2, padx=5, pady=5, sticky="nsew")
        
        # self.updateCanvas()
        self.canvas.bind("<Button-1>", self.selectBall)

        scrollbarInfo_v = Scrollbar(self.drawPanel)
        scrollbarInfo_h = Scrollbar(self.drawPanel, orient=HORIZONTAL)
        self.infobox = Text(self.drawPanel,width=42,height=6,yscrollcommand=scrollbarInfo_v.set, xscrollcommand=scrollbarInfo_h.set, wrap=NONE)
        self.infobox.grid(row=4,column=0,rowspan=1,columnspan=2, padx=5, pady=5, sticky="nsew")

        self.list = Canvas(self.drawPanel, width=self.width, height=self.height, bg="white", highlightthickness=0)
        self.list.grid(row=5,column=0,rowspan=3,columnspan=2)

        scrollbarList5_v = Scrollbar(self.list)
        scrollbarList5_h = Scrollbar(self.list, orient=HORIZONTAL)
        self.list5 = Listbox(self.list,width=21,height=10,yscrollcommand=scrollbarList5_v.set, xscrollcommand=scrollbarList5_h.set, highlightthickness=0)
        self.list5.grid(row=0, column=0, padx=5, pady=5, sticky="nsew")

        scrollbarList34_v = Scrollbar(self.list)
        scrollbarList34_h = Scrollbar(self.list, orient=HORIZONTAL)
        self.list34 = Listbox(self.list,width=21,height=10,yscrollcommand=scrollbarList34_v.set, xscrollcommand=scrollbarList34_h.set, highlightthickness=0)
        self.list34.grid(row=0, column=1, padx=5, pady=5, sticky="nsew")

        self.simuPanel = Canvas(self, highlightthickness=0)
        self.simuPanel.grid(row=0, column=2, padx=10, pady=10, sticky="nsew")
        
        self.figure = Figure(figsize = (4,3), dpi = 100)
        self.plot = self.figure.add_subplot(111)
        self.canvas_tk_agg = FigureCanvasTkAgg(self.figure, master=self.simuPanel)
        self.canvas_tk_agg.get_tk_widget().grid(row=0,column=0,rowspan=4,columnspan=2, padx=5, pady=5, sticky="nsew")
        self.simu_plot_toolbar = NavigationToolbar2Tk(self.canvas_tk_agg, self.simuPanel, pack_toolbar=False)
        self.simu_plot_toolbar.grid(row=4,column=0,rowspan=1,columnspan=2, padx=5, pady=5, sticky="nsew")

        self.strategyInput = Canvas(self.simuPanel, width=self.width, height=self.height, highlightthickness=0)
        self.strategyInput.grid(row=5,column=0,rowspan=1,columnspan=2, padx=5, pady=5, sticky="nsew")
        label=Label(self.strategyInput, text="Drawing strategy: ")
        label.grid(row=0, column=0, padx=5, pady=5, sticky="w")
        Entry(self.strategyInput, textvariable=self.strategyStr).grid(row=0, column=1, padx=5, pady=5, sticky="w")
        Button(self.strategyInput, text="...", 
                command=lambda textVar=self.strategyStr:self.selectStrategy(textVar)).grid(row=0, column=2, padx=5, pady=5, sticky="w")

        self.stopInput = Canvas(self.simuPanel, width=self.width, height=self.height, highlightthickness=0)
        self.stopInput.grid(row=6,column=0,rowspan=1,columnspan=2, padx=5, pady=5, sticky="nsew")
        label=Label(self.stopInput, text="Stop when: ")
        label.grid(row=0, column=0, padx=5, pady=5, sticky="w")
        Entry(self.stopInput, textvariable=self.stopStr).grid(row=0, column=1, padx=5, pady=5, sticky="w")
        Button(self.stopInput, text="...", 
                command=lambda textVar=self.stopStr:self.selectStop(textVar)).grid(row=0, column=2, padx=5, pady=5, sticky="w")
        Checkbutton(self.stopInput, highlightthickness=0, text="full exp", variable=self.fullexpmode, onvalue=True, offvalue=False
            ).grid(row=0, column=3, padx=5, pady=5, sticky="w")

        self.simuNumInput = Canvas(self.simuPanel, width=self.width, height=self.height, highlightthickness=0)
        self.simuNumInput.grid(row=7,column=0,rowspan=1,columnspan=2, padx=5, pady=5, sticky="nsew")
        label=Label(self.simuNumInput, text="Simulation number: ")
        label.grid(row=0, column=0, padx=5, pady=5, sticky="w")
        Entry(self.simuNumInput, textvariable=self.simu_num).grid(row=0, column=1, padx=5, pady=5, sticky="w")

        self.simuButton = Button(self.simuPanel, text='simulate',width=20,command=self.simu)
        self.simuButton.grid(row=8,column=0,rowspan=1,columnspan=1, padx=5, pady=5, sticky="nsew")
        self.simuplotswitchbuttons = Canvas(self.simuPanel, highlightthickness=0)
        self.simuplotswitchbuttons.grid(row=9, column=0, rowspan=1,columnspan=4, padx=5, pady=5, sticky="nsew")
        Button(self.simuplotswitchbuttons, text='histogram',width=12,command=self.draw_simu_hist).grid(row=0,column=0,rowspan=1,columnspan=1, padx=5, pady=5, sticky="nsew")
        Button(self.simuplotswitchbuttons, text='density curve',width=12,command=self.draw_simu_density).grid(row=0,column=1,rowspan=1,columnspan=1, padx=5, pady=5, sticky="nsew")
        Button(self.simuplotswitchbuttons, text='cumulative distribution',width=20,command=self.draw_simu_distribution).grid(row=0,column=2,rowspan=1,columnspan=1, padx=5, pady=5, sticky="nsew")
        self.binsInput = Canvas(self.simuPanel, highlightthickness=0)
        self.binsInput.grid(row=10, column=0, padx=5, pady=5, sticky="nsew")
        label=Label(self.binsInput, text="bins:")
        label.grid(row=0, column=0, padx=5, pady=5, sticky="w")
        Entry(self.binsInput, textvariable=self.hist_bins, width=6).grid(row=0, column=1, padx=5, pady=5, sticky="w")

        scrollbardebug_v = Scrollbar(self.simuPanel)
        scrollbardebug_h = Scrollbar(self.simuPanel, orient=HORIZONTAL)
        self.debugbox = Text(self.simuPanel,width=42,height=5,yscrollcommand=scrollbardebug_v.set, xscrollcommand=scrollbardebug_h.set, wrap=NONE)
        self.debugbox.grid(row=11,column=0,rowspan=1,columnspan=2, padx=5, pady=5, sticky="nsew")

    def inputConfirm(self):
        self.initialize()
        self.updateCanvas()
        self.updateStatistics()
        self.plot.clear()
    
    def updateStatistics(self):
        self.updateInfo()
        self.updateList()

    def updateInfo(self):
        self.infobox.delete('1.0', END)
        probs = self.gacha.cprobs
        ts = "  ".join(["%s:%.2f%%" % (rank, probs[rank]*100) for rank in probs.keys()])+"\n"
        ts += "Consumed Orbs:\t%d" % (self.orbs)
        for rank in ['5u', '5', '4to5', 's4to5', '4u', '34']:
            ts += "\n%s:\t%d" % ({'5u':'5*up', '5':'5*', '4to5':'4->5', 's4to5':'s 4->5', '4u':'4*up', '34':'34*'}[rank], len(self.statistics[rank]))

        self.infobox.insert('1.0', ts)
    
    def debug_print(self, *args, **kwargs):
        ts = ' '.join([str(_) for _ in args]) + '\n'
        self.debugbox.insert(END, ts)
    
    def updateList(self):
        self.list5.delete(0, END)
        self.list5.insert(END, "5*")
        for rank in ['5u','5','4to5','s4to5']:
            counter = collections.Counter(self.statistics[rank])
            for k in counter.keys():
                self.list5.insert(END, "%s: %d"%(k,counter[k]))
        self.list5.insert(END, "")
        self.list5.insert(END, "DETAILS")
        for rank in ['5u','5','4to5','s4to5']:
            for i in self.statistics[rank]:
                self.list5.insert(END, i)
        
        self.list34.delete(0, END)
        self.list34.insert(END, "34*")
        for rank in ['4u','34']:
            counter = collections.Counter(self.statistics[rank])
            for k in counter.keys():
                self.list34.insert(END, "%s: %d"%(k,counter[k]))
        self.list5.insert(END, "")
        self.list34.insert(END, "DETAILS")
        for rank in ['4u','34']:
            for i in self.statistics[rank]:
                self.list34.insert(END, i)
    
    def selectChara(self, color, textVar):
        newWindow = Toplevel(self)
        panel = charaPanel(newWindow, textVar)
        panel.initialization(setting={"color": set([color])})
        panel.updateResult()
        panel.updateCharas()

    def update_CHEAT(self):
        self.updateCheatingInfoonCanvas()
    
    def selectMode(self, event):
        self.mode = MODES.index(self.modeselectbox.get())

    def parseUserInput(self, up=None, mode=None):
        if not up:
            up = self.up
        if not mode:
            mode = self.mode
        
        charas = {'5u':[], '4u':[]}
        for pup in ['5u', '4u']:
            for color in COLORS:
                charaStr = up[pup][color]
                if type(charaStr) is not str:
                    charaStr = charaStr.get()
                for chara in charaStr.split(","):
                    if chara != "":
                        charas[pup].append({'name': chara, 'color': color})

        if type(mode) is not int:
            mode = mode.get()
        mode = MODES[mode]
        if mode in ["normal", "special"]:
            if "4u" in list(charas.keys()) and len(charas['4u'])>0:
                probs = {"5u": 0.03, "5": 0.03, "4to5": 0.03, "4u": 0.03, "34": 0.88}
            else:
                probs = {"5u": 0.03, "5": 0.03, "4to5": 0.03, "34": 0.91}
        elif mode in ["special 4*"]:
            if "4u" in list(charas.keys()) and len(charas['4u'])>0:
                probs = {"5u": 0.03, "5": 0.03, "4to5": 0.03, "s4to5":0.03, "4u": 0.03, "34": 0.85}
            else:
                probs = {"5u": 0.03, "5": 0.03, "4to5": 0.03, "s4to5":0.03, "34": 0.88}
        elif mode in ["herofest"]:
            probs = {"5u": 0.05, "5": 0.03, "4to5": 0.03, "34": 0.89}
        elif mode in ["double"]:
            if "4u" in list(charas.keys()) and len(charas['4u'])>0:
                probs = {"5u": 0.06, "4to5": 0.03, "4u": 0.03, "34": 0.88}
            else:
                probs = {"5u": 0.06, "4to5": 0.03, "34": 0.91}
        elif mode in ["legendary"]:
            probs = {"5u": 0.08, "4to5": 0.03, "34": 0.89}
        elif mode in ["weekly"]:
            probs = {"5u": 0.04, "5": 0.02, "4to5": 0.03, "34": 0.91}
        
        return probs, charas

    def updateCanvas(self):
        self.canvas.delete("all")
        for i in range(len(self.balls)):
            imgpath = os.path.join(IMGPATH, "util", "%s"%self.colorList[i])
            imgpath = addImgExt(imgpath)
            x0 = (self.balls[i][0]+self.balls[i][2])/2
            y0 = (self.balls[i][1]+self.balls[i][3])/2
            if os.path.exists(imgpath):
                self.ballImgHolder[i] = PhotoImage(file=imgpath)
                self.canvas.create_image(x0, y0,image=self.ballImgHolder[i], tags=("balls"))
            else:
                self.canvas.create_oval(*self.balls[i], fill=self.colorList[i], tags=("balls"))
            self.updateCheatingInfoonCanvas()
    
    def updateCheatingInfoonCanvas(self):
        self.canvas.delete("cheating")
        for i in range(len(self.balls)):
            x0 = (self.balls[i][0]+self.balls[i][2])/2
            y0 = (self.balls[i][1]+self.balls[i][3])/2
            if self.cheatmode.get() and self.round[i]:
                self.canvas.create_text(x0, y0, text=self.round[i]['name']+'  '+self.round[i]['rank'], tags=("charas_name", "cheating"))
    
    def selectBall(self, event):
        def inBox(x1,y1,x2,y2, x,y):
            return x>x1 and x<x2 and y>y1 and y<y2
        s=-1
        for i in range(len(self.balls)):
            if inBox(*self.balls[i], event.x, event.y):
                s = i
                break
        Nonenum = 0
        for i in range(len(self.balls)):
            if self.round[i] is None:
                Nonenum += 1
        if s == -1:
            if Nonenum == 0:
                return
            self.round = self.gacha.rollARound()
            self.colorList = [c['color'] for c in self.round]
            self.updateCanvas()
        else:
            if self.round[s] is None:
                pass
            else:
                self.gacha.processingSelection(self.round, [s])

                # draw background
                imgpath = os.path.join(IMGPATH, "util", "charatemplate_bg_%dstar" % {'5u':5, '5':5, '4to5':5, 's4to5':5, '4u': 4, '34':4}[self.round[s]['rank']])
                imgpath = addImgExt(imgpath)
                if os.path.exists(imgpath):
                    img = Image.open(imgpath)
                    img = img.resize((70, 70))
                    self.charaBgHolder[s] = ImageTk.PhotoImage(img)
                    self.canvas.create_image((self.balls[s][0]+self.balls[s][2])/2, (self.balls[s][1]+self.balls[s][3])/2, image=self.charaBgHolder[s], tags=("charasBg"))
                else:
                    pass
                
                # draw character
                imgpath = os.path.join(IMGPATH, "chara", "%s" % (self.round[s]['name']))
                imgpath = addImgExt(imgpath)
                if os.path.exists(imgpath):
                    if self.round[s]['rank'] in ['5u', '4u'] and not NOPIL:
                        img = Image.open(imgpath)
                        img = img.resize((60, 60))
                        self.charaImgHolder[s] = ImageTk.PhotoImage(img)
                    else:
                        self.charaImgHolder[s] = PhotoImage(file=imgpath)
                    self.canvas.create_image((self.balls[s][0]+self.balls[s][2])/2, (self.balls[s][1]+self.balls[s][3])/2, image=self.charaImgHolder[s], tags=("charas"))
                else:
                    self.canvas.create_text((self.balls[s][0]+self.balls[s][2])/2, (self.balls[s][1]+self.balls[s][3])/2, text=self.round[s]['name']+'  '+self.round[s]['rank'], tags=("charas_name"))
                
                # draw border
                imgpath = os.path.join(IMGPATH, "util", "charatemplate_border_%dstar" % {'5u':5, '5':5, '4to5':5, 's4to5':5, '4u': 4, '34':4}[self.round[s]['rank']])
                imgpath = addImgExt(imgpath)
                if os.path.exists(imgpath):
                    img = Image.open(imgpath)
                    img = img.resize((70, 70))
                    self.charaBorderHolder[s] = ImageTk.PhotoImage(img)
                    self.canvas.create_image((self.balls[s][0]+self.balls[s][2])/2, (self.balls[s][1]+self.balls[s][3])/2, image=self.charaBorderHolder[s], tags=("charasBg"))
                else:
                    pass

                self.orbs += [5,4,4,4,3][Nonenum]
                self.statistics[self.round[s]['rank']].append(self.round[s]['name'])
                # self.colorList[s] = self.round[s]['name']
                self.round[s] = None
        
        self.updateCheatingInfoonCanvas()
        self.updateStatistics()
        # print(self.gacha.cprobs, self.gacha.count, self.gacha.lantern)
    
    def selectStrategy(self, textVar):
        newWindow = Toplevel(self)
        panel = strategyPanel(newWindow, textVar)
        panel.initialization()
        # panel.updateResult()
        # panel.updateCharas()
    
    def selectStop(self, textVar):
        newWindow = Toplevel(self)
        panel = stopPanel(newWindow, textVar)
        panel.initialization()
        # panel.updateResult()
        # panel.updateCharas()

    def simu_parseStrategy(self, colorList):
        strategyStr = self.strategyStr.get()
        wanted = []
        unwanted = []
        for c in strategyStr:
            if c in ['R','B','G','W']:
                wanted.append({'R':'red', 'B':'blue', 'G':'green', 'W':'gray'}[c])
            elif c in ['r','b','g','w']:
                unwanted.append({'r':'red', 'b':'blue', 'g':'green', 'w':'gray'}[c])
        ret = []
        for i,color in enumerate(colorList):
            if color in wanted:
                ret.append(i)
        if len(ret) == 0:
            for color in unwanted:
                if color in colorList:
                    ret.append(colorList.index(color))
                    break
        return ret
    
    def simu_parseStrategyCheat(self, round):
        strategyStr = self.strategyStr.get()
        rankList = [ch['rank'] for ch in round]
        wanted = []
        unwanted = []
        for r in strategyStr.split(" "):
            if r in ['5u','5','4to5','s4to5','4u','34']:
                wanted.append(r)
        unwanted = [r for r in ['5u','5','4to5','s4to5','4u','34'] if r not in wanted]
        ret = []
        for i,r in enumerate(rankList):
            if r in wanted:
                ret.append(i)
        if len(ret) == 0:
            for r in unwanted:
                if r in rankList:
                    ret.append(rankList.index(r))
                    break
        return ret

    def simu_parseStop(self, collection):
        if not self.fullexpmode:
            return eval(self.compiled_simuStopFunc, {'collection': collection})
        else:
            return self.parser.eval(collection, exp_tree=self.stopExpTree)
    
    def compile_simuStopFunc(self):
        stopStr = self.stopStr.get()
        if not self.fullexpmode:
            exp = self.parser.translatePresetting(stopStr, self.parseUserInput()[1]['5u'])  # parse [ ]
            self.debug_print(exp)
            exp = self.parser.translateName(exp, self.data["heroes"]+self.tmpdata["heroes"])    # parse name
            self.debug_print(exp)
            self.compiled_simuStopFunc = safecompile(exp)
        else:
            exp = self.parser.translatePresetting(stopStr, self.parseUserInput()[1]['5u'])  # parse [ ]
            self.debug_print(exp)
            self.stopExpTree = self.parser.parse(exp)
            self.debug_print(self.stopExpTree)
    
    class simu_thread(threading.Thread):
        def __init__(self, name, app, cheatmode):
            threading.Thread.__init__(self)
            self.name = name
            self.app = app
            self.cheatmode = cheatmode
        def run(self):
            self.app.simuSTOP = False
            self.app.compile_simuStopFunc()
            if self.cheatmode:
                self.app.simulationObj.strategy = self.app.simu_parseStrategyCheat
                self.app.simu_orbres = self.app.simulationObj.simu_withInfo(int(self.app.simu_num.get()))
            else:
                self.app.simulationObj.strategy = self.app.simu_parseStrategy
                self.app.simu_orbres = self.app.simulationObj.simu(int(self.app.simu_num.get()))
    
    class simu_result_update(threading.Thread):
        def __init__(self, simu, app):
            threading.Thread.__init__(self)
            self.simu = simu
            self.app = app
        def run(self):
            while self.simu.is_alive():
                time.sleep(0.1)
            self.app.draw_simu_hist()
            self.app.print_statistics()
            self.app.simuButton.config(text="simulate")
            self.app.is_simulating = False

    def simu(self):
        if not self.is_simulating:
            self.is_simulating = True
            self.simuButton.config(text="terminate")
            self.simurunning = self.simu_thread("1", self, self.cheatmode.get())
            self.simuupdating = self.simu_result_update(self.simurunning, self)
            self.simurunning.start()
            self.simuupdating.start()
        else:
            self.simuSTOP = True
            # self.simuButton.config(text="simulate")
            # self.is_simulating = False
    
    def draw_simu_hist(self, bins=20):
        if not self.simu_orbres:
            return
        try:
            bins = int(self.hist_bins.get())
        except Exception as e:
            self.debug_print("Invalid bins:", bins)
            self.debug_print(type(e), e)
        self.plot.clear()
        self.plot.hist(self.simu_orbres, bins=bins)
        self.canvas_tk_agg.draw()
        self.simu_plot_toolbar.update()
    
    def draw_simu_density(self):
        if not self.simu_orbres:
            return
        x = list(range(0, max(self.simu_orbres)+1))
        y = densitycurve(x, self.simu_orbres)
        self.plot.clear()
        self.plot.plot(x, y)
        self.canvas_tk_agg.draw()
        self.simu_plot_toolbar.update()
    
    def draw_simu_distribution(self):
        if not self.simu_orbres:
            return
        x = list(range(0, max(self.simu_orbres)+1))
        y = distributioncurve(x, self.simu_orbres)
        self.plot.clear()
        self.plot.plot(x, y)
        self.canvas_tk_agg.draw()
        self.simu_plot_toolbar.update()
    
    def print_statistics(self):
        if not self.simu_orbres:
            return
        mean = lambda a:sum(a)/len(a)
        miu = mean(self.simu_orbres)
        sigma = (mean([(i-miu)**2 for i in self.simu_orbres]))**0.5
        self.debug_print(miu)
        self.debug_print(miu-sigma, miu+sigma)
        self.debug_print(miu-sigma*2, miu+sigma*2)
        self.debug_print(miu-sigma*3, miu+sigma*3)






if __name__ == "__main__":
    root = Tk()
    root.geometry('1200x800+200+300')
    root.title('')
    app = Application(master=root)
    app.update()
    
    root.mainloop()