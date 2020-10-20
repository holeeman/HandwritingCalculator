# -*- coding: utf-8 -*-
from network import Network
from PIL import Image
from tensorflow.keras import preprocessing
from tensorflow.keras import utils
import matplotlib.pyplot as plt
import cv2
import numpy as np

def load_img(file, sqsize=(500,500)):
    size = sqsize
    cvim = cv2.imread(file)
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
    return preprocessing.image.img_to_array(img)

if __name__ == "__main__":
    # initialize recognition network
    recognitionNetwork = Network()
    recognitionNetwork.load("recognition_model")
    test_image = load_img('data/1/1.png')
    plt.imshow(test_image)
    plt.show()
    print(test_image.shape)
    test_label = utils.to_categorical(np.array([5]), 22)
    print(test_label.shape)
    score=recognitionNetwork.model.evaluate(np.array([test_image])/255, test_label, verbose=2)
    print(score)
