import cv2
import numpy as np
from PIL import Image
from Pipeline import Pipe

def hss(arr):
    if len(arr) == 0:
        return
    if len(arr) == 1:
        return arr[0][1]
    groups = []
    group = []
    maxx = -1
    for i in range(0,len(arr)-1):
        group.append(arr[i])
        x, _, w, _ = arr[i][0]
        if x + w > maxx:
            maxx = x + w
        x2 = arr[i+1][0][0]
        if maxx < x2:
            groups.append(group)
            group = []
            maxx = -1
    group.append(arr[-1])
    groups.append(group)
    
    hstr = ""
    for g in groups:
        if list(map(lambda x: x[1], g))[0] == "sqrt":
            hstr += sqss(g)
        else:
            hstr += vss(g)
    return hstr

def sqss(arr):
    if len(list(filter(lambda x:x[1] =="sqrt", arr))) == 0:
        return eqss(arr)
    filtered = list(filter(lambda x:x[1] !="sqrt", arr))
    return f"sqrt({hss(filtered)})"

def eqss(arr):
    if len(list(filter(lambda x:x[1] == "-", arr))) == 2:
        return "="
    else:
        return "".join(map(lambda x:x[1],arr))

def vss(arr):
    if len(arr) == 0:
        return ""
    if len(arr) == 1:
        return arr[0][1]
    fracs = list(filter(lambda x:x[1] =="-", arr))
    if len(fracs) == 0:
        return sqss(arr)
    frac = max(fracs, key=lambda x:x[0][2])
    mid = frac[0][1]
    top = []
    bottom = []
    for s in arr:
        if s==frac:
            continue
        if s[0][1] < mid:
            top.append(s)
        else:
            bottom.append(s)
    if len(top) == 0 and len(bottom) == 0:
        return "-"
    elif len(top) == 0:
        return sqss(arr)
    elif len(bottom) == 0:
        return sqss(arr)

    return f"({hss(top)})/({hss(bottom)})"

class Parser(Pipe):
    def __init__(self):
        pass

    def exec(self, arg=None):
        if arg:
            return self.parse(arg)
        return None
    
    def parse(self, arr):
        if arr == 0:
            return ""
        return hss(sorted(arr, key=lambda x:x[0][0]))