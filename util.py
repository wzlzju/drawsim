import os
import collections, copy, functools
import re
import pyparsing
from const import *
from util import *
try:
    from PIL import Image, ImageTk, ImageDraw, ImageFont
    import numpy as np
    NOPIL = False
except:
    NOPIL = True


def addImgExt(path):
    imgext = [".png", ".PNG", ".jpg", ".jpeg", ".JPG", ".bmp", ".BMP", ".webp"]
    for ext in imgext:
        imgpath = path + ext
        if os.path.exists(imgpath):
            break
        imgpath = path + ".png"
    return imgpath

def getimage(holders=None, label=None, size=(60, 60)):
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
    img = ImageTk.PhotoImage(img)
    if holders is not None:
        holders.append(img)
    else:
        return img

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


def safecompile(string):
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
    return code

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

def dict_merge(a, b):
    return {**a, **b}

def is_iterable(obj):  
    try:  
        iter(obj)  
        return True  
    except TypeError:  
        return False  

class stopParser(object):
    def __init__(self):
        and_ = pyparsing.Keyword('and')
        or_ = pyparsing.Keyword('or')
        not_ = pyparsing.Keyword('not')
        true_ = pyparsing.Keyword('True')
        false_ = pyparsing.Keyword('False')

        not_op = not_ | '~'
        and_op = and_ | '&'
        or_op = or_ | '|'

        intNum = pyparsing.pyparsing_common.signed_integer()

        self.expr = pyparsing.Forward()

        self.word = ~(and_ | or_ | not_ | true_ | false_) + \
                pyparsing.Word(pyparsing.alphas) + \
                pyparsing.ZeroOrMore(pyparsing.Group('('+pyparsing.OneOrMore(pyparsing.Word(pyparsing.alphas))+')'))
                # pyparsing.ZeroOrMore(pyparsing.Group('('+pyparsing.Word(pyparsing.alphas)+')')) + \
                # pyparsing.ZeroOrMore(pyparsing.Group('('+pyparsing.Word(pyparsing.alphas)+pyparsing.Word(pyparsing.alphas)+')'))
                # pyparsing.ZeroOrMore(pyparsing.Group(' '+'('+pyparsing.Word(pyparsing.alphas)+pyparsing.ZeroOrMore(pyparsing.Group(' '+pyparsing.Word(pyparsing.alphas)))+')'))
                # pyparsing.ZeroOrMore(pyparsing.Group(' '+'('+pyparsing.Word(pyparsing.alphas)+')')) + \
                # pyparsing.ZeroOrMore(pyparsing.Group(' '+'('+pyparsing.Word(pyparsing.alphas)+' '+pyparsing.Word(pyparsing.alphas)+')'))
        name = pyparsing.originalTextFor(self.word[1, ...]).setName("name")
        operator = pyparsing.oneOf("== != < > >= <= eq ne lt le gt ge", caseless=True) | pyparsing.Empty().addParseAction(lambda: ">=")
        condition = pyparsing.Group(name + operator + intNum).setName("condition")
        presetting = pyparsing.Group('[' + pyparsing.oneOf("all any") + pyparsing.oneOf("red blue green gray") + intNum + ']').setName("presetting")

        identifier =  condition | presetting
        atom = identifier | pyparsing.Group('(' + self.expr + ')') | true_ | false_
        factor = pyparsing.Group(pyparsing.ZeroOrMore(not_op) + atom)
        term = pyparsing.Group(factor + pyparsing.ZeroOrMore(and_op + factor))
        self.expr <<= pyparsing.Group(term + pyparsing.ZeroOrMore(or_op + term))
    
    def parse(self, s):
        return self.expr.parseString(s)
    
    def runTests(self, s):
        self.expr.runTests(s)
    
    def dump(self, tree):
        def _dump_rec(tree):
            if not self.is_iterable(tree):
                return tree
            res = ""
            for i, e in enumerate(tree):
                e = _dump_rec(e)
                e = str(e).strip()
                if e not in [')', ']']:
                    res += e
                else:
                    res = res[:-1] + e
                if e not in ['(', '['] and i<len(tree)-1:
                    res += ' '
            return res
        return _dump_rec(tree)
    
    def eval(self, collection, exp=None, exp_tree=None):
        assert exp or exp_tree, "exp must be provided"
        assert not (exp and exp_tree), "both exp and tree are provided"

        exp_tree = exp_tree if exp_tree is not None else self.parse(exp)

        def _eval_rec(collection, tree, rec_depth=-1):
            operands = []
            operator = None
            if self.is_iterable(tree) and len(tree)==3 and type(tree[0]) is str and tree[1] in "== != > < >= <=".split() and type(tree[2]) is int:
                name = tree[0].strip()
                value1 = collection.get(name, 0)
                cmp = self.operator_convert(tree[1])
                value2 = tree[2]
                return eval("%d %s %d" % (value1, cmp, value2))
            for e in tree:
                if self.is_iterable(e):
                    operands.append(_eval_rec(collection, e, rec_depth=rec_depth+1))
                elif e in ["True", "False"]:
                    operands.append(eval(e))
                elif e in ["and", "or", "not"]:
                    operator = e
                elif e in ['(', ')']:
                    pass
                elif e in ['[', ']']:
                    raise Exception("Unhandled presetting.")
                else:
                    raise Exception("Unidentified identifiers: '%s'"%e)
            if operator == "not":
                ret = not operands[0]
            elif operator == "and":
                ret = functools.reduce(lambda x,y: x and y, operands)
            elif operator == "or":
                ret = functools.reduce(lambda x,y: x or y, operands)
            elif operator == None:
                ret = operands[0]
            return ret

        return _eval_rec(collection, exp_tree, rec_depth=0)
    
    def reform(self, tree):
        def _reform_rec(tree):
            operands = []
            operator = None
            if self.is_iterable(tree) and len(tree)==3 and type(tree[0]) is str and tree[1] in "== != > < >= <=".split() and type(tree[2]) is int:
                name = tree[0].strip()
                cmp = self.operator_convert(tree[1])
                value = tree[2]
                return {
                    "op": cmp,
                    "obj": [name, value]
                }
            if self.is_iterable(tree) and len(tree)==5 and tree[0]=='[' and tree[-1]==']':
                operator = tree[1]
                color = tree[2]
                value = tree[3]
                return {
                    "op": operator,
                    "obj": [color, value]
                }
            for e in tree:
                if self.is_iterable(e):
                    operands.append(_reform_rec(e))
                elif e in ["True", "False"]:
                    operands.append(e)
                elif e in ["and", "or", "not"]:
                    operator = e
                elif e in ['(', ')']:
                    pass
                elif e in ['[', ']']:
                    raise Exception("Unhandled presetting.")
                else:
                    raise Exception("Unidentified identifiers: '%s'"%e)
            if operator is None:
                return operands[0]
            return {
                "op": operator,
                "obj": operands
            }
        return _reform_rec(tree)
    
    def reform_back(self, tree):
        def _refome_back_res(node):
            if type(node) is str:
                return node
            op = node["op"]
            obj = node["obj"]
            if op in ["all", "any"]:
                return ['[']+[op]+obj+[']']
            if op in "== != < > <= >=".split():
                return [obj[0], op, obj[1]]
            if op in ["not"]:
                return [op, '(', _refome_back_res(obj[0]), ')']     # only the first operand under "not" makes sense
            if op in ["and", "or"]:
                res = [_refome_back_res(obj[0])]
                for e in obj[1:]:
                    res.append(op)
                    res.append(_refome_back_res(e))
                return ['(']+res+[')']
        return _refome_back_res(tree)

    def is_iterable(self, obj):
        return type(obj) is pyparsing.results.ParseResults or type(obj) is list

    def operator_convert(self, op):
        if op in "== != < > <= >=":
            return op
        return {
            "eq": "==",
            "nt": "!=",
            "le": "<=",
            "lt": "<",
            "ge": ">=",
            "gt": ">",
        }[op]

    def translatePresetting(self, s, charas):
        exp = ""
        while True:
            i = s.find('[')
            if i == -1:
                exp += s
                break
            exp += s[:i]
            s = s[i+1:]
            j = s.find(']')
            if j == -1:
                j = len(s)
            tmp = s[:j]
            s = s[j+1:]
            identifier = tmp.strip().split()[0].lower()
            color = tmp.strip().split()[1].lower()
            num = int(tmp.strip().split()[2])
            ttmp = {'all':' and ','any':' or '}[identifier].join(["%s %d"%(c['name'],num) for c in charas if c['color']==color])
            if ttmp == "":
                ttmp = "True"
            exp += "(%s)"%ttmp
        return exp
    
    def translateName(self, exp, charas):
        for hero in charas:
            name = hero["name"]
            pexp = copy.deepcopy(exp)
            exp = ""
            while True:
                i = pexp.find(name)
                if i == -1:
                    exp += pexp
                    break
                j = i+len(name)
                if pexp[j:].lstrip()[0:1].isnumeric() and (i==0 or pexp[i-1] in [' ','(']):
                    exp += pexp[:i]
                    exp += "collection.get('%s',0) >="%name
                else:
                    k = pexp[j:].find(' ')
                    if k != -1:
                        j += k
                    exp += pexp[:j]
                pexp = pexp[j:]
        return exp


if __name__ == "__main__":
    p = stopParser()
    s = "((Veyle >= 11 and Edelgard (Winter) >= 11 and Seidr (New Year) >= 10) or (Veyle >= 11 and Edelgard (Winter) >= 10 and Seidr (New Year) >= 11) or (Veyle >= 10 and Edelgard (Winter) >= 11 and Seidr (New Year) >= 11))"
    # res = p.word.runTests("Seidr(M) (fm) (New Year)")
    res = p.parse(s)
    print(res)
    print(p.dump(res))
    print(p.reform(res))
    print(p.reform_back(p.reform(res)))
    print(p.dump(p.reform_back(p.reform(res))))
    res = p.parse("[all red 11] and [all blue 10] and [all green 10] and True")
    print(p.dump(res))
    print(p.reform(res))
    print(p.reform_back(p.reform(res)))
    print(p.dump(p.reform_back(p.reform(res))))
    print(res, type(res))
    c = {
        "a(b) (c)": 10,
        "b(b) (c)": 9,
        "c(b) (c)": 10
    }
    res = p.eval(c, exp="True and (a(b) (c) >= 10 and b(b) (c) >= 10 and c(b) (c) >= 10)")
    print(res)
    print(p.dump(res))