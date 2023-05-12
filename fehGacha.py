import random, math

from fehdata import data

class gacha(object):
    def __init__(self, 
                probs={"5u": 0.03, "5": 0.03, "4to5": 0.03, "34": 0.91}, # 5u, 5, 4u, 4to5, 34
                charas={"5u": [{'name':'po', 'color': 'gray'}], "5": None, "4to5": None, "34": None},
                mode="normal"):
        self.probs = probs
        for prank in ['5u', '5', '4u', '4to5', '34']:
            if prank not in list(self.probs.keys()):
                self.probs[prank] = 0.0
        self.charas = charas
        self.charas['5'] = [{
            'name': c['name'],
            'color': c['color']
        } for c in data['heroes'] if c['rating'] in [6, 16]]
        self.charas['4to5'] = [{
            'name': c['name'],
            'color': c['color']
        } for c in data['heroes'] if c['rating'] in [3, 30]]
        self.charas['34'] = [{
            'name': c['name'],
            'color': c['color']
        } for c in data['heroes'] if c['rating'] in [2, 20]]
        self.mode = mode

        self.cprobs = self.probs
        self.count = 0
        self.lantern = 0

    def rollARound(self):
        round = [None] * 5
        for i in range(5):
            charaRank = random.choices(list(self.cprobs.keys()), list(self.cprobs.values()))[0]
            chara = random.choice(self.charas[charaRank])
            round[i] = chara
            round[i]['rank'] = charaRank
        return round
    
    def processingSelection(self, round, selections):
        for s in selections:
            crank = round[s]
            self.count += 1
            if self.count % 5 == 0:
                p5 = self.cprobs['5u']+self.cprobs['5']+0.005
                self._updateProbability(p5)
            if self.count >= 120:
                p5 = 1.0
                self._updateProbability(p5)
            if crank == "5u":
                self.cprobs = self.probs
                self.count = 0
                if self.lantern >= 3:
                    self.lantern = 0
            elif crank == "5":
                p5 = self.cprobs['5u']+self.cprobs['5']-0.02
                if p5 < self.probs['5u']+self.probs['5']:
                    p5 = self.probs['5u']+self.probs['5']
                self._updateProbability(p5)
                self.count = 0
                self.lantern += 1
            if self.lantern >= 3: # to disable lantern mechanism, set self.lantern == math.inf
                self.cprobs['5u'] = self.cprobs['5u']+self.cprobs['5']
                self.cprobs['5'] = 0.0
    
    def _updateProbability(self, p5):
        pnon5 = 1-p5
        self.cprobs['5u'] = p5*self.probs['5u']/(self.probs['5u']+self.probs['5'])
        self.cprobs['5'] = p5*self.probs['5']/(self.probs['5u']+self.probs['5'])
        self.cprobs['4to5'] = pnon5*self.probs['4to5']/(self.probs['4u']+self.probs['4to5']+self.probs['34'])
        self.cprobs['4u'] = pnon5*self.probs['4u']/(self.probs['4u']+self.probs['4to5']+self.probs['34'])
        self.cprobs['34'] = pnon5*self.probs['34']/(self.probs['4u']+self.probs['4to5']+self.probs['34'])

class drawing(object):
    def __init__(self, up, mode="normal"):
        self.mode = mode
        if mode in ["normal", "special"]:
            if "4u" in list(up.keys()):
                probs = {"5u": 0.03, "5": 0.03, "4to5": 0.03, "4u": 0.03, "34": 0.88}
            else:
                probs = {"5u": 0.03, "5": 0.03, "4to5": 0.03, "34": 0.91}
        elif mode in ["herofest"]:
            probs = {"5u": 0.05, "5": 0.03, "4to5": 0.03, "34": 0.89}
        elif mode in ["double"]:
            print(up)
            if "4u" in list(up.keys()):
                probs = {"5u": 0.06, "4to5": 0.03, "4u": 0.03, "34": 0.88}
            else:
                probs = {"5u": 0.06, "4to5": 0.03, "34": 0.91}
        elif mode in ["legendary"]:
            probs = {"5u": 0.08, "4to5": 0.03, "34": 0.89}
        charas = up
        self.gacha = gacha(probs=probs,
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
    
    def draw(self):
        round = self.gacha.rollARound()
        colorList = [c['color'] for c in round]
        print(colorList)
        for i in range(5):
            s = input()
            if s not in ['1','2','3','4','5']:
                if i==0:
                    i -= 1
                    continue
                else:
                    break
            s = int(s)
            if round[s-1] is None:
                i -= 1
                continue
            else:
                self.orbs += [5,4,4,4,3][i]
                print(round[s-1]['name'], '\t', round[s-1]['rank'])
                self.statistics[round[s-1]['rank']].append(round[s-1]['name'])
                colorList[s-1] = round[s-1]['name']
                round[s-1] = None
                print(colorList)



class drawsimulation(object):
    def __init__(self, gacha, strategy, terminate):
        self.gacha = gacha
        self.strategy = strategy
        self.terminate = terminate
    
    def simu(self, N=10000):
        orbres = []
        for i in range(N):
            orbs = 0
            collection = {}
            while True:
                round = self.gacha.rollARound()
                colorList = [c['color'] for c in round]
                selection = self.strategy(colorList)
                orbs += [5,5+4,5+4+4,5+4+4+4,5+4+4+4+3][len(selection)-1]
                charas = [round[s]['name'] for s in selection]
                for c in charas:
                    if c in list(collection.keys()):
                        collection[c] += 1
                    else:
                        collection[c] = 1
                if self.terminate(collection):
                    break
            orbres.append(orbs)
        return orbres
            


if __name__ == "__main__":
    draw = drawing(up={'5u':[{
                            "name": "依娜拉",
                            "color": "red"
                        },
                        {
                            "name": "古尔维格",
                            "color": "gray"
                        },
                        {
                            "name": "鲁弗莱",
                            "color": "blue"
                        },
                        {
                            "name": "塞内里奥",
                            "color": "green"
                        }]},
                    mode="normal")
    for i in range(10):
        draw.draw()
    print("Orbs:", draw.orbs)
    print("Statistics: 5: %d, 34: %d" % (len(draw.statistics['5u']+draw.statistics['5']+draw.statistics['4to5']), len(draw.statistics['4u']+draw.statistics['34'])))
    print("5Star:", draw.statistics['5u']+draw.statistics['5']+draw.statistics['4to5'])
        