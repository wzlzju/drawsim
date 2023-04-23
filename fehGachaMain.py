from tkinter import *
from tkinter import messagebox
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
import random, math, re

import fehGacha as gacha

COLORS = ["red", "blue", "green", "gray"]
MODES = ["normal", "special", "herofest", "double", "legendary", "weekly"]

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
                'red': StringVar(self, "依娜拉"),
                'blue': StringVar(self, "鲁弗莱"),
                'green': StringVar(self, "塞内里奥"),
                'gray': StringVar(self, "古尔维格")
            },
            '4u':{
                'red': StringVar(self, ""),
                'blue': StringVar(self, ""),
                'green': StringVar(self, ""),
                'gray': StringVar(self, "")
            }
        }
        
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
        
        # self.balls = [
        #     (125,25,175,75),
        #     (55,75,105,125),
        #     (90,165,140,215),
        #     (170,165,220,215),
        #     (195,75,245,125)
        # ]

        self.strategyStr = StringVar(self, "Rwgb")
        self.stopStr = StringVar(self, "依娜拉 11 or 古尔维格 11")
        self.simu_num = StringVar(self, "1000")

        self.initialize()
        self.createWidget()

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

    def createWidget(self):
        self.inputPanel = Canvas(self)
        self.inputPanel.grid(row=0, column=0)

        rowId = 0
        for pup in ['5u', '4u']:
            for color in COLORS:
                self.upInput = Canvas(self.inputPanel)
                self.upInput.grid(row=rowId,column=0)
                label=Label(self.upInput, text="%s %s: " % ({'5u':"5* Up", '4u':"4* Up"}[pup], color))
                label.grid(row=0, column=0)
                entry=Entry(self.upInput, textvariable=self.up[pup][color])
                entry.grid(row=0, column=1)
                rowId += 1
        
        self.modeInput = Canvas(self.inputPanel)
        self.modeInput.grid(row=rowId,column=0)
        label=Label(self.modeInput, text="Gacha type:")
        label.grid(row=0, column=0)
        for i, mode in enumerate(MODES):
            radio=Radiobutton(self.modeInput, text=mode, value=i, variable=self.mode)
            radio.grid(row=i+1, column=0)
        Button(self.inputPanel, text='confirm',width=8,command=self.inputConfirm).grid(row=rowId+1,column=0)

        self.drawPanel = Canvas(self)
        self.drawPanel.grid(row=0, column=1)

        self.canvas = Canvas(self.drawPanel, width=self.width, height=self.height, bg="white")
        self.canvas.grid(row=0,column=0,rowspan=4,columnspan=2)
        
        self.updateCanvas()
        # self.canvas.tag_bind("balls", "<Button-1>", self.selectBall)
        self.canvas.bind("<Button-1>", self.selectBall)

        scrollbarInfo_v = Scrollbar(self.drawPanel)
        # scrollbarInfo_v.pack(side=RIGHT, fill=Y)
        scrollbarInfo_h = Scrollbar(self.drawPanel, orient=HORIZONTAL)
        # scrollbarInfo_h.pack(side=BOTTOM, fill=X)
        self.infobox = Text(self.drawPanel,width=42,height=6,yscrollcommand=scrollbarInfo_v.set, xscrollcommand=scrollbarInfo_h.set, wrap=NONE)
        self.infobox.grid(row=4,column=0,rowspan=1,columnspan=2)

        self.list = Canvas(self.drawPanel, width=self.width, height=self.height, bg="white")
        self.list.grid(row=5,column=0,rowspan=3,columnspan=2)

        scrollbarList5_v = Scrollbar(self.list)
        # scrollbarList5_v.pack(side=RIGHT, fill=Y)
        scrollbarList5_h = Scrollbar(self.list, orient=HORIZONTAL)
        # scrollbarList5_h.pack(side=BOTTOM, fill=X)
        self.list5 = Listbox(self.list,width=21,height=10,yscrollcommand=scrollbarList5_v.set, xscrollcommand=scrollbarList5_h.set)
        self.list5.grid(row=0, column=0)

        scrollbarList34_v = Scrollbar(self.list)
        # scrollbarList34_v.pack(side=RIGHT, fill=Y)
        scrollbarList34_h = Scrollbar(self.list, orient=HORIZONTAL)
        # scrollbarList34_h.pack(side=BOTTOM, fill=X)
        self.list34 = Listbox(self.list,width=21,height=10,yscrollcommand=scrollbarList34_v.set, xscrollcommand=scrollbarList34_h.set)
        self.list34.grid(row=0, column=1)

        self.simuPanel = Canvas(self)
        self.simuPanel.grid(row=0, column=2)
        
        self.figure = Figure(figsize = (4,3), dpi = 100)
        self.plot = self.figure.add_subplot(111)
        self.canvas_tk_agg = FigureCanvasTkAgg(self.figure, master=self.simuPanel)
        self.canvas_tk_agg.get_tk_widget().grid(row=0,column=0,rowspan=4,columnspan=2)

        self.strategyInput = Canvas(self.simuPanel, width=self.width, height=self.height)
        self.strategyInput.grid(row=4,column=0,rowspan=1,columnspan=2)
        label=Label(self.strategyInput, text="Drawing strategy: ")
        label.grid(row=0, column=0)
        Entry(self.strategyInput, textvariable=self.strategyStr).grid(row=0, column=1)

        self.stopInput = Canvas(self.simuPanel, width=self.width, height=self.height)
        self.stopInput.grid(row=5,column=0,rowspan=1,columnspan=2)
        label=Label(self.stopInput, text="Stop when: ")
        label.grid(row=0, column=0)
        Entry(self.stopInput, textvariable=self.stopStr).grid(row=0, column=1)
        # self.stopInput = Entry(self, textvariable=self.stopStr).grid(row=5,column=2,rowspan=1,columnspan=2)

        self.simuNumInput = Canvas(self.simuPanel, width=self.width, height=self.height)
        self.simuNumInput.grid(row=6,column=0,rowspan=1,columnspan=2)
        label=Label(self.simuNumInput, text="Simulation number: ")
        label.grid(row=0, column=0)
        Entry(self.simuNumInput, textvariable=self.simu_num).grid(row=0, column=1)
        # self.simuNumInput = Entry(self, textvariable=self.simu_num).grid(row=6,column=2,rowspan=1,columnspan=2)

        Button(self.simuPanel, text='simulate',width=8,command=self.simu).grid(row=7,column=0,rowspan=1,columnspan=1)
        
    def inputConfirm(self):
        self.initialize()
        self.updateCanvas()
        self.updateStatistics()
        self.plot.clear()
    
    def updateStatistics(self):
        # self.after(100, self.updateInfo)
        # self.after(100, self.updateList)
        self.updateInfo()
        self.updateList()

    def updateInfo(self):
        self.infobox.delete('1.0', END)
        ts = "Consumed Orbs:\t%d" % (self.orbs)
        for rank in ['5u', '5', '4to5', '4u', '34']:
            ts += "\n%s:\t%d" % ({'5u':'5*up', '5':'5*', '4to5':'4->5', '4u':'4*up', '34':'34*'}[rank], len(self.statistics[rank]))

        self.infobox.insert('1.0', ts)
        # self.after(100, self.updateInfo)
    
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
        
        # self.after(100, self.updateList)

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
                for chara in charaStr.split():
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
        self.canvas.create_rectangle(0,0,self.width,self.height, fill="white", outline="white", tags=("canvas_bg"))
        for i in range(len(self.balls)):
            self.canvas.create_oval(*self.balls[i], fill=self.colorList[i], tags=("balls"))
    
    def selectBall(self, event):
        # messagebox.showinfo('message', 'select ball1')
        # print(event.widget)
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
                self.orbs += [5,4,4,4,3][Nonenum]
                self.canvas.create_text((self.balls[s][0]+self.balls[s][2])/2, (self.balls[s][1]+self.balls[s][3])/2, text=self.round[s]['name']+'  '+self.round[s]['rank'])
                # print(self.round[s]['name'], '\t', self.round[s]['rank'])
                self.statistics[self.round[s]['rank']].append(self.round[s]['name'])
                self.colorList[s] = self.round[s]['name']
                self.round[s] = None
                # print(self.colorList)
                # print(self.orbs)
        
        self.updateStatistics()
    
    def simu_selectStrategy(self, colorList):
        strategyStr = self.strategyStr.get()
        wanted = []
        unwanted = []
        for c in strategyStr:
            if c == c.upper() and c in ['R','B','G','W']:
                wanted.append({'R':'red', 'B':'blue', 'G':'green', 'W':'gray'}[c])
            elif c == c.lower() and c in ['r','b','g','w']:
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

    def simu_stopStrategy(self, collection):
        stopStr = self.stopStr.get()
        exp = stopStr.split(' ')
        for i in range(len(exp)):
            if exp[i] not in ['and', 'or'] and not exp[i].isdigit():
                exp[i] = "collection.get('%s',0) >=" % (exp[i])
        return eval(" ".join(exp))
    
    def simu(self):
        orbres = self.simulationObj.simu(int(self.simu_num.get()))
        self.plot.clear()
        self.plot.hist(orbres, bins=20)
        self.canvas_tk_agg.draw()




if __name__ == "__main__":
    root = Tk()
    root.geometry('1200x800+200+300')
    root.title('')
    app = Application(master=root)
    app.update()
    
    root.mainloop()