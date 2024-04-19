import os
import collections
import re


def addImgExt(path):
    imgext = [".png", ".PNG", ".jpg", ".jpeg", ".JPG", ".bmp", ".BMP", ".webp"]
    for ext in imgext:
        imgpath = path + ext
        if os.path.exists(imgpath):
            break
        imgpath = path + ".png"
    return imgpath


def densitycurve(x=None, samples=None):
    if not samples:
        return
    if not x:
        x = list(range(min(samples), max(samples)+1))
    num = len(samples)
    counter = collections.Counter(samples)
    return [counter[i]/num for i in x]

def masscurve(x=None, samples=None, PDF=None):
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