import sqlite3 as sqlite

conn = sqlite.connect("cards.cdb")
cursor = conn.cursor()
query = cursor.execute("select id, setcode, alias from datas")
cards=[(r[0], r[1], r[2]) for r in query]

cc = {}
ids = set()
for id, code, alias in cards:
	if id in ids:
		continue
	ids.add(id)
	if alias != 0:
		continue
	cs = hex(code)[2:]
	while True:
		css = cs[-4:]
		cs = cs[:-4]
		css = css.zfill(4)
		if css[:1] != "0":
			tcss = "0"+css[1:]
			if cc.get(tcss, None) is None:
				cc[tcss] = 0
			cc[tcss] += 1
		if cc.get(css, None) is None:
			cc[css] = 0
		cc[css] += 1
		if len(cs)==0:
			break

c2t = {}
with open("strings.conf", "r", encoding="utf-8", errors="ignore") as f:
	for line in f:
		if not line.startswith("!setname 0x") and not line.startswith("#setname 0x") and not line.startswith("#!setname 0x"):
			continue
		spos = line.find(" 0x")
		s = line[spos+1:]
		ls = s.split()
		splitpos = s.find(" ")
		code = int(ls[0], 16)#int(s[:splitpos], 16)
		name = ls[1]#s[splitpos+1:]
		c2t[code] = name
		
cd = [(c2t.get(int(a,16), "0x"+a),"0x"+a, cc[a]) if a!="0000" else ("————","0",cc[a]) for a in cc.keys()]
cd.sort(key=lambda x:x[-1], reverse=True)

s = ""
for k, q, v in cd:
	s += k.replace("\n", "") + "\t" + q +"\t" + str(v) + "\n"
with open("archetypesnumrank.txt", "w", encoding="utf-8") as f:
	f.write(s)