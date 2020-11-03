import tensorflow as tf
from tensorflow.keras import preprocessing
import os
import cv2
from random import randint
from PIL import Image
from PIL import ImageFilter
import matplotlib.pyplot as plt
import numpy as np

def preprocess():
    image = []
    label = []
    name = []
    size = (500, 500)
    count = 0
    label_i = 0
    for folder_name in os.listdir("data"):
        folder_path = os.path.join("data", folder_name)
        index = 0
        for fname in os.listdir(folder_path):
            name.append(folder_name)
            fpath = os.path.join(folder_path, fname)
            # rename files
            # newname = str(index)+".png"
            # newpath = os.path.join(folder_path,newname)
            # os.rename(fpath, newpath)
            cvim = cv2.imread(fpath)
            kern = np.ones((3,3), np.uint8)
            cvim = cv2.erode(cvim,kern, iterations=8)
            cvim = cv2.cvtColor(cvim, cv2.COLOR_BGR2RGB)
            im = Image.fromarray(cvim)
            res = Image.new('RGB', size, (255,255,255))
            w, h = im.size
            offset = ((size[0]-w) // 2, (size[1]-h) // 2)
            res.paste(im, offset)
            res = res.resize((100,100))
            img = preprocessing.image.array_to_img(res)
            tensor = preprocessing.image.img_to_array(img)
            label.append(label_i)
            image.append(tensor)
            index += 1
            count += 1
        label_i += 1
    return np.array([i for i in image]), np.array([l for l in label])

if __name__ == "__main__":
    preprocess()