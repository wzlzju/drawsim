import random
import matplotlib.pyplot as plt

global p5, chains, orb, rank5counts

character_pool = {
	"5": ["r5a", "r5b", "r5c", "b5a", "b5b", "b5c", "g5a", "g5b", "g5c", "w5a", "w5b", "w5c"],
	"4": ["r4x"]*38 + ["b4x"]*43 + ["g4x"]*32 + ["w4x"]*40
}

target = ["g", "b", "r", "w"]
needed_orbs = [5, 4, 4, 4, 3]

def generateARound():
	global  p5
	res = [None] * 5
	for i in range(5):
		r = random.random()
		if r <= p5:
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
	global p5, chains, orb, rank5counts
	if len(results) == 0:
		results.append(0)
	for i in range(len(results)):
		chains += 1
		orb += needed_orbs[i]
		color = colors[results[i]]
		rank = ranks[results[i]]
		character = characters[results[i]]
		if rank == "5":
			p5 = 0.08
			chains = 0
			if color == target[0]:
				if character in list(targetcounts.keys()):
					rank5counts[character] += 1
		else:
			if chains >= 5:
				p5 += 0.005
				chains -= 5
				if p5 >= 0.20:
					p5 = 1
				
if __name__ == "__main__":
	global p5, chains, orb, rank5counts
	full_bl_1 = []
	full_bl_2 = []
	full_bl_3 = []
	num_3fbl_1 = []
	num_3fbl_2 = []
	num_3fbl_3 = []
	num_3fbl_all = []
	
	for sim_num in range(10000):
		p5 = 0.08
		chains = 0
		orb = 0
		rank5counts = {"a": 0, "b": 0, "c": 0}
		
		while(True):
			colors, ranks, characters = generateARound()
			results = gachaStrategy(colors)
			processResults(colors, ranks, characters, results)
			full_bl_num = sum([i >= 11 for i in list(rank5counts.values())])
			if full_bl_num >= 1 and len(full_bl_1) == sim_num:
				full_bl_1.append(orb)
			if full_bl_num >= 2 and len(full_bl_2) == sim_num:
				full_bl_2.append(orb)
			if full_bl_num >= 3 and len(full_bl_3) == sim_num:
				full_bl_3.append(orb)
				l = list(rank5counts.values())
				l.sort()
				num_3fbl_1.append(max(l))
				num_3fbl_2.append(l[1])
				num_3fbl_3.append(min(l))
				num_3fbl_all.append(sum(l))
				break
	
	mean = lambda x: sum(x)/len(x)
	
	miu = mean(full_bl_1)
	sigma = (mean([(i-miu)**2 for i in full_bl_1]))**0.5
	print(miu)
	print(miu-sigma, miu+sigma)
	print(miu-sigma*2, miu+sigma*2)
	print(miu-sigma*3, miu+sigma*3)
	plt.hist(full_bl_1, bins=20)
	plt.title("full break limit 1 rank5")
	plt.xlabel("orbs")
	plt.ylabel("num")
	plt.show()
	
	miu = mean(full_bl_2)
	sigma = (mean([(i-miu)**2 for i in full_bl_2]))**0.5
	print(miu)
	print(miu-sigma, miu+sigma)
	print(miu-sigma*2, miu+sigma*2)
	print(miu-sigma*3, miu+sigma*3)
	plt.hist(full_bl_2, bins=20)
	plt.title("full break limit 2 rank5")
	plt.xlabel("orbs")
	plt.ylabel("num")
	plt.show()
	
	miu = mean(full_bl_3)
	sigma = (mean([(i-miu)**2 for i in full_bl_3]))**0.5
	print(miu)
	print(miu-sigma, miu+sigma)
	print(miu-sigma*2, miu+sigma*2)
	print(miu-sigma*3, miu+sigma*3)
	plt.hist(full_bl_3, bins=20)
	plt.title("full break limit 3 rank5")
	plt.xlabel("orbs")
	plt.ylabel("num")
	plt.show()
	
	#plt.hist(num_3fbl_1, bins=20)
	#plt.title("other rank5 num after 3 fbl")
	#plt.xlabel("num 1")
	#plt.ylabel("num")
	#plt.show()
	
	#plt.hist(num_3fbl_2, bins=20)
	#plt.title("other rank5 num after 3 fbl")
	#plt.xlabel("num 2")
	#plt.ylabel("num")
	#plt.show()
	
	#plt.hist(num_3fbl_3, bins=20)
	#plt.title("other rank5 num after 3 fbl")
	#plt.xlabel("num 3")
	#plt.ylabel("num")
	#plt.show()
	
	#plt.hist(num_3fbl_all, bins=20)
	#plt.title("other rank5 num after 3 fbl")
	#plt.xlabel("num all")
	#plt.ylabel("num")
	#plt.show()