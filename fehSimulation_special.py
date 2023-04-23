import random
import matplotlib.pyplot as plt

global p5u, p4u, p5, chains, orb, targetcounts

character_pool = {
	"5u": ["r5a", "b5a", "g5a", "w5a"],
	"4u": ["b4a"],
	"5": ["r5x"]*33 + ["b5x"]*28 + ["g5x"]*22 + ["w5x"]*20,
	"4": ["r4x"]*38 + ["b4x"]*43 + ["g4x"]*32 + ["w4x"]*40
}

target = ["r", "w", "g", "b"]
needed_orbs = [5, 4, 4, 4, 3]

def generateARound():
	global  p5u, p4u, p5
	res = [None] * 5
	for i in range(5):
		r = random.random()
		if r <= p5u:
			res[i] = random.choice(character_pool["5u"])
		elif r <= p5u + p4u:
			res[i] = random.choice(character_pool["4u"])
		elif r <= p5u + p4u +p5:
			res[i] = random.choice(character_pool["5"])
		else:
			res[i] = random.choice(character_pool["4"])
	return [i[0] for i in res], [i[1] for i in res], [i[-1] for i in res]

def gachaStrategy(colors):
	res = []
	if target[0] in colors:
		for i in range(5):
			if colors[i] == target[0]:
				res.append(i)
	else:
		for c in target[1:]:
			if c in colors:
				for i in range(5):
					if colors[i] == c:
						res.append(i)
						break
				break
	return res

def processResults(colors, ranks, characters, results):
	global p5u, p4u, p5, chains, orb, targetcounts
	if len(results) == 0:
		results.append(0)
	for i in range(len(results)):
		chains += 1
		orb += needed_orbs[i]
		color = colors[results[i]]
		rank = ranks[results[i]]
		character = characters[results[i]]
		if rank == "5":
			if character != "x":
				p5u = 0.03
				p4u = 0.03
				p5 = 0.03
				chains = 0
				if color == target[0]:
					if character in list(targetcounts.keys()):
						targetcounts[character] += 1
			else:
				p5u = 0.03 if p5u <= 0.04 else p5u-0.01
				p5 = p5u
				p4u = (1-p5u-p5)*0.03/(1-0.03-0.03)
				chains = 0
		else:
			if character != "x":
				if color == target[0]:
					targetcounts[character] += 1
			if chains >= 5:
				p5u += 0.0025
				p5 = p5u
				p4u = (1-p5u-p5)*0.03/(1-0.03-0.03)
				chains -= 5
				if p5u >= 0.09:
					p5u = 0.5
					p5 = 0.5
					p4u = 0
				
if __name__ == "__main__":
	global p5u, p4u, p5, chains, orb, targetcounts
	full_bl_1 = []
	
	for sim_num in range(10000):
		p5u = 0.03
		p4u = 0.03
		p5 = 0.03
		chains = 0
		orb = 0
		targetcounts = {"a": 0}
		
		while(True):
			colors, ranks, characters = generateARound()
			results = gachaStrategy(colors)
			processResults(colors, ranks, characters, results)
			if targetcounts["a"] >= 11:
				full_bl_1.append(orb)
				break
	
	mean = lambda x: sum(x)/len(x)
	
	miu = mean(full_bl_1)
	sigma = (mean([(i-miu)**2 for i in full_bl_1]))**0.5
	print(miu)
	print(miu-sigma, miu+sigma)
	print(miu-sigma*2, miu+sigma*2)
	print(miu-sigma*3, miu+sigma*3)
	plt.hist(full_bl_1, bins=20)
	plt.title("full break limit 1")
	plt.xlabel("orbs")
	plt.ylabel("num")
	plt.show()