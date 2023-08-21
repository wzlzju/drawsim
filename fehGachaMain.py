from tkinter import *
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import random, math, re, os

import fehGacha as gacha
try:
    from PIL import Image, ImageTk
    NOPIL = False
except:
    NOPIL = True

COLORS = ["red", "blue", "green", "gray"]
MODES = ["normal", "special", "herofest", "double", "legendary", "weekly"]
IMGPATH = "./img"


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
        self.stopStr = StringVar(self, "Corrin(F) (Brave) 9 and Gullveig (Brave) 10 or Corrin(F) (Brave) 10 and Gullveig (Brave) 9")
        self.simu_num = StringVar(self, "1000")

        self.initialize()
        self.createWidget()
        self.inputConfirm()

    def initialize(self):
        probs, charas = self.parseUserInput(self.up, self.mode)

        self.gacha = gacha.gacha(probs=probs,
                            charas=charas,
                            mode=self.mode)
        self.statistics = {
            '5u': [],
            '5': [],
            '4u': [],
            '4to5': [],
            '34': []
        }
        self.orbs = 0

        self.round = self.gacha.rollARound()
        self.colorList = [c['color'] for c in self.round]

        
        self.simulationObj = gacha.drawsimulation(
                                gacha=gacha.gacha(
                                    probs=probs,
                                    charas=charas,
                                    mode=self.mode
                                ),
                                strategy=self.simu_selectStrategy,
                                terminate=self.simu_stopStrategy
                            )
        
        self.ballImgHolder = [None]*5
        self.charaImgHolder = [None]*5
        self.charaBgHolder = [None]*5
        self.charaBorderHolder = [None]*5
    
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
                rowId += 1
        
        self.modeInput = Canvas(self.inputPanel, highlightthickness=0)
        self.modeInput.grid(row=1, column=0, padx=5, pady=5, sticky="w")
        label=Label(self.modeInput, text="Gacha type:")
        label.grid(row=0, column=0)
        for i, mode in enumerate(MODES):
            radio=Radiobutton(self.modeInput, text=mode, value=i, variable=self.mode)
            radio.grid(row=i+1, column=0, padx=5, pady=5, sticky="w")
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

        self.strategyInput = Canvas(self.simuPanel, width=self.width, height=self.height, highlightthickness=0)
        self.strategyInput.grid(row=4,column=0,rowspan=1,columnspan=2, padx=5, pady=5, sticky="nsew")
        label=Label(self.strategyInput, text="Drawing strategy: ")
        label.grid(row=0, column=0, padx=5, pady=5, sticky="w")
        Entry(self.strategyInput, textvariable=self.strategyStr).grid(row=0, column=1, padx=5, pady=5, sticky="w")

        self.stopInput = Canvas(self.simuPanel, width=self.width, height=self.height, highlightthickness=0)
        self.stopInput.grid(row=5,column=0,rowspan=1,columnspan=2, padx=5, pady=5, sticky="nsew")
        label=Label(self.stopInput, text="Stop when: ")
        label.grid(row=0, column=0, padx=5, pady=5, sticky="w")
        Entry(self.stopInput, textvariable=self.stopStr).grid(row=0, column=1, padx=5, pady=5, sticky="w")

        self.simuNumInput = Canvas(self.simuPanel, width=self.width, height=self.height, highlightthickness=0)
        self.simuNumInput.grid(row=6,column=0,rowspan=1,columnspan=2, padx=5, pady=5, sticky="nsew")
        label=Label(self.simuNumInput, text="Simulation number: ")
        label.grid(row=0, column=0, padx=5, pady=5, sticky="w")
        Entry(self.simuNumInput, textvariable=self.simu_num).grid(row=0, column=1, padx=5, pady=5, sticky="w")

        Button(self.simuPanel, text='simulate',width=8,command=self.simu).grid(row=7,column=0,rowspan=1,columnspan=1, padx=5, pady=5, sticky="nsew")

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
        ts = "Consumed Orbs:\t%d" % (self.orbs)
        for rank in ['5u', '5', '4to5', '4u', '34']:
            ts += "\n%s:\t%d" % ({'5u':'5*up', '5':'5*', '4to5':'4->5', '4u':'4*up', '34':'34*'}[rank], len(self.statistics[rank]))

        self.infobox.insert('1.0', ts)
    
    def updateList(self):
        self.list5.delete(0, END)
        self.list5.insert(END, "5*")
        for i in self.statistics['5u']:
            self.list5.insert(END, i)
        for i in self.statistics['5']:
            self.list5.insert(END, i)
        for i in self.statistics['4to5']:
            self.list5.insert(END, i)
        
        self.list34.delete(0, END)
        self.list34.insert(END, "34*")
        for i in self.statistics['4u']:
            self.list34.insert(END, i)
        for i in self.statistics['34']:
            self.list34.insert(END, i)
    
    def update_CHEAT(self):
        self.updateCanvas()

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
            if os.path.exists(imgpath):
                self.ballImgHolder[i] = PhotoImage(file=imgpath)
                x0 = (self.balls[i][0]+self.balls[i][2])/2
                y0 = (self.balls[i][1]+self.balls[i][3])/2
                self.canvas.create_image(x0, y0,image=self.ballImgHolder[i], tags=("balls"))
            else:
                self.canvas.create_oval(*self.balls[i], fill=self.colorList[i], tags=("balls"))
            if self.cheatmode.get():
                self.canvas.create_text(x0, y0, text=self.round[i]['name']+'  '+self.round[i]['rank'], tags=("charas"))
    
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
                imgpath = os.path.join(IMGPATH, "util", "charatemplate_bg_%dstar" % {'5u':5, '5':5, '4to5':5, '4u': 4, '34':4}[self.round[s]['rank']])
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
                    self.canvas.create_text((self.balls[s][0]+self.balls[s][2])/2, (self.balls[s][1]+self.balls[s][3])/2, text=self.round[s]['name']+'  '+self.round[s]['rank'], tags=("charas"))
                
                # draw border
                imgpath = os.path.join(IMGPATH, "util", "charatemplate_border_%dstar" % {'5u':5, '5':5, '4to5':5, '4u': 4, '34':4}[self.round[s]['rank']])
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
                self.colorList[s] = self.round[s]['name']
                self.round[s] = None
        
        self.updateStatistics()
        # print(self.gacha.cprobs, self.gacha.count, self.gacha.lantern)
    
    def simu_selectStrategy(self, colorList):
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
    
    def simu_selectStrategyCheat(self, round):
        strategyStr = self.strategyStr.get()
        rankList = [ch['rank'] for ch in round]
        wanted = []
        unwanted = []
        for r in strategyStr.split(" "):
            if r in ['5u','5','4to5','4u','34']:
                wanted.append(r)
        unwanted = [r for r in ['5u','5','4to5','4u','34'] if r not in wanted]
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

    def simu_stopStrategy(self, collection):
        stopStr = self.stopStr.get()
        parse_or = stopStr.split(" or ")
        for i, exp_or in enumerate(parse_or):
            parse_and = exp_or.split(" and ")
            for j, exp_and in enumerate(parse_and):
                exps = exp_and.split(" ")
                exp = ("collection.get('%s',0) >=" % (" ".join(exps[:-1])))+" "+exps[-1]
                parse_and[j] = exp
            exp = " and ".join(parse_and)
            parse_or[i] = exp
        exp = " or ".join(parse_or)
        return safeeval(exp, {'collection': collection})

        # exp = stopStr.split()
        # for i in range(len(exp)):
        #     if exp[i] not in ['and', 'or', 'not'] and not exp[i].isdigit():
        #         exp[i] = "collection.get('%s',0) >=" % (exp[i])
        # return safeeval(" ".join(exp), {'collection': collection})
    
    def simu(self):
        if self.cheatmode.get():
            self.simulationObj.strategy = self.simu_selectStrategyCheat
            orbres = self.simulationObj.simu_withInfo(int(self.simu_num.get()))
        else:
            self.simulationObj.strategy = self.simu_selectStrategy
            orbres = self.simulationObj.simu(int(self.simu_num.get()))
        self.plot.clear()
        self.plot.hist(orbres, bins=20)
        self.canvas_tk_agg.draw()

def safeeval(string, dict) :
    code = compile(string,'<user input>','eval')
    reason = None
    banned = ('eval','compile','exec','getattr','hasattr','setattr','delattr',
            'classmethod','globals','help','input','isinstance','issubclass','locals',
            'open','print','property','staticmethod','vars')
    for name in code.co_names:
        if re.search(r'^__\S*__$',name):
            reason = 'dunder attributes not allowed'
        elif name in banned:
            reason = 'arbitrary code execution not allowed'
        if reason:
            raise NameError(f'{name} not allowed : {reason}')
    return eval(code, dict)

def addImgExt(path):
    imgext = [".png", ".PNG", ".jpg", ".jpeg", ".JPG", ".bmp", ".BMP", ".webp"]
    for ext in imgext:
        imgpath = path + ext
        if os.path.exists(imgpath):
            break
        imgpath = path + ".png"
    return imgpath


if __name__ == "__main__":
    root = Tk()
    root.geometry('1200x800+200+300')
    root.title('')
    app = Application(master=root)
    app.update()
    
    root.mainloop()