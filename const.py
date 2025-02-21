TRANSPARENTCOLOR = "#abcdef"
COLORS = ["red", "blue", "green", "gray"]
WEAPONS = ["sword", "lance", "axe", "staff", "redtome", "bluetome", "greentome", "graytome", 
            "redbow", "bluebow", "greenbow", "graybow", "reddagger", "bluedagger", "greendagger", "graydagger", 
            "reddragon", "bluedragon", "greendragon", "graydragon", "redbeast", "bluebeast", "greenbeast", "graybeast"]
MOVES = ["infantry", "armored", "flying", "cavalry"]
VERSIONS = [1, 2, 3, 4, 5, 6, 7, 8]
GAMES = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15]
MODES = ["normal", "special", "special 4*", "herofest", "double", "legendary", "weekly"]
OPTIONS = {"color": COLORS, "move": MOVES, "weapon": WEAPONS, "version": VERSIONS, "game": GAMES}
IMGPATH = "./img"
FULLSTOPFUNC = True
CMPOPS = ">= > <= < == !=".split()
LOGICOPS = "and or not".split()
PRESETTINGOPS = "all any".split()
OP2TX = {"and":"All","or":"Any","not":"Not","all":"<all>","any":"<any>"}
for cmp in CMPOPS:
    OP2TX[cmp] = cmp
TX2OP = {OP2TX[k]:k for k in OP2TX.keys()}
OPCOLORS_BG = {
    "and": "misty rose",
    "or": "light cyan",
    "not": "light yellow",
    "all": "misty rose",
    "any": "light cyan",
    "default": "gray90",
    "others": "gray90",
}

