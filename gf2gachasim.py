import random
import collections
import matplotlib.pyplot as plt


INIT_P = 0.006
BDSTART = 59
BDEND = 80
UP_IN_5_P = 0.5
BBD = 2

def P(d):
    if d < BDSTART:
        return INIT_P
    else:
        return (d-BDSTART+1)/(BDEND-BDSTART+1)*(1-INIT_P) + INIT_P

def drawonce():
    sum = 0
    for BDTIME in range(1, BBD+1):
        for i in range(1, BDEND+1):
            p = P(i)
            if random.random() < p:
                sum += i
                break
        if BDTIME==BBD or random.random()<UP_IN_5_P:
            break

    return sum

def drawsim(N=10000):
    return [drawonce() for _ in range(N)]

def densitycurve(x=None, samples=None):
    if not samples:
        return
    if not x:
        x = list(range(min(samples), max(samples)+1))
    num = len(samples)
    counter = collections.Counter(samples)
    return [counter[i]/num for i in x]

def distributioncurve(x=None, samples=None, PDF=None):
    if not samples:
        return
    if not x:
        x = list(range(min(samples), max(samples)+1))
    if not PDF:
        PDF = densitycurve(x, samples)
    return [sum(PDF[:i+1]) for i in range(len(PDF))]

def drawprobabilitycurve(draws):
    x = list(range(1, BDEND*BBD+1))
    y = densitycurve(x, draws)
    plt.plot(x, y)
    plt.show()

    y = distributioncurve(x, draws, PDF=y)
    plt.plot(x, y)
    plt.show()

def printstatistics(samples, RANGE=None):
    miu = sum(samples)/len(samples)
    sigma = (sum([(sample-miu)**2 for sample in samples])/len(samples))**0.5
    if not RANGE:
        RANGE = list(range(-3,4))
    print("%f   "*len(RANGE)%tuple(miu+i*sigma for i in RANGE))


if __name__ == "__main__":
    N = 1000000
    draws = drawsim(N=N)
    printstatistics(draws, RANGE=[0])
    drawprobabilitycurve(draws)
