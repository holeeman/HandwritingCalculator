'''
@author: Hosung Lee
@date: December 2 2020
@description: Preprocesing code
'''

import tensorflow as tf
from tensorflow.keras import preprocessing
import os
import cv2
from random import randint
from PIL import Image
from PIL import ImageFilter
import matplotlib.pyplot as plt
import numpy as np

def calcit(size):
    if size < 50:
        return -1
    return (size - 50)//30

def removepad(cvim):
    gray=cv2.cvtColor(cvim,cv2.COLOR_BGR2GRAY)
    gray = cv2.bitwise_not(gray)
    contours, hierarchy = cv2.findContours(gray,cv2.RETR_LIST,cv2.CHAIN_APPROX_SIMPLE)[-2:]
    minx, miny, maxx, maxy = (float("inf"),float("inf"),-1,-1)
    for cnt in contours:
        x,y,w,h = cv2.boundingRect(cnt)
        if x < minx:
            minx = x
        if y < miny:
            miny = y
        if x+w > maxx:
            maxx = x+w
        if y+h > maxy:
            maxy = y+h
    return cvim[miny:maxy, minx:maxx]

def preprocess():
    newSize = (100, 100)
    newratio = 1.3
    mathdata = []
    for datadir in ["data","testdata"]:
        print(datadir)
        image = []
        label = []
        label_i = 0
        for folder_name in os.listdir(datadir):
            print(folder_name,)
            folder_path = os.path.join(datadir, folder_name)
            index = 0
            for fname in os.listdir(folder_path):
                fpath = os.path.join(folder_path, fname)
                # rename files
                # newname = str(index)+".png"
                # newpath = os.path.join(folder_path,newname)
                # os.rename(fpath, newpath)
                
                im = cv2.imread(fpath)
                im = removepad(im)
                h, w, c = im.shape
                nh, nw = (int(max(h,w)*newratio), int(max(h,w)*newratio))
                resized = np.full((nh, nw, c), (255, 255, 255), dtype=np.uint8)
                x = (nw - w) // 2
                y = (nh - h) // 2
                resized[y:y+h, x:x+w] = im
                cvim = cv2.cvtColor(resized, cv2.COLOR_BGR2RGB)
                it = calcit(nh)
                if it > 0:
                    cvim = cv2.erode(cvim, np.ones((3,3), np.uint8), iterations=it)
                elif it < 0:
                    cvim = cv2.erode(cvim, np.ones((3,3), np.uint8), iterations=-it)
                cvim = cv2.resize(cvim, newSize)
                pilim = Image.fromarray(cvim)
                img = preprocessing.image.array_to_img(pilim)
                tensor = preprocessing.image.img_to_array(img)
                label.append(label_i)
                image.append(tensor)
                index += 1
            label_i += 1
        mathdata.append((np.array([i for i in image]), np.array([l for l in label])))

if __name__ == "__main__":
    preprocess()