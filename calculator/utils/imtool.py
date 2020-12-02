'''
@author: Hosung Lee
@date: December 2 2020
@description: Image tool for preprocess
'''

from PIL import Image
from tensorflow.keras import preprocessing
import numpy as np
import cv2

class ImageSetting:
    newRatio = 1.3
    newSize = (100, 100)

def calcit(size):
    #print(size)
    if size < 50:
        return 0
    return (size - 50)//30

def convertImage(image):
    h, w, c = image.shape
    nh, nw = (int(max(h,w)*ImageSetting.newRatio), int(max(h,w)*ImageSetting.newRatio))
    resized = np.full((nh, nw, c), (255, 255, 255), dtype=np.uint8)
    x = (nw - w) // 2
    y = (nh - h) // 2
    resized[y:y+h, x:x+w] = image
    cvim = cv2.cvtColor(resized, cv2.COLOR_BGR2RGB)
    it = calcit(nh)
    if it > 0:
        cvim = cv2.erode(cvim, np.ones((3,3), np.uint8), iterations=it)
    elif it < 0:
        cvim = cv2.dilate(cvim, np.ones((3,3), np.uint8), iterations=-it)
    cvim = cv2.resize(cvim, ImageSetting.newSize)
    im = Image.fromarray(cvim)
    img = preprocessing.image.array_to_img(im)
    arr = preprocessing.image.img_to_array(img)
    return cvim