'''
@author: Hosung Lee
@date: December 2 2020
@description: Extractor class
'''

import cv2
import numpy as np
from PIL import Image
from calculator.utils.pipeline import Pipe

class Extractor(Pipe):
    def __init__(self, classifier=None):
        self.classifier = classifier
    
    def exec(self, arg=None):
        return self.extract(arg)

    def extract(self, img):
        pim = Image.open(img)
        img = cv2.cvtColor(np.array(pim), cv2.COLOR_RGB2BGR)
        res = img.copy()
        img = cv2.bitwise_not(img)
        _, thresh = cv2.threshold(cv2.cvtColor(img,cv2.COLOR_BGR2GRAY), 127, 255, 0)
        contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        extracted = []
        
        for i in range(len(contours)):
            x, y, w, h = cv2.boundingRect(contours[i])
            mask = np.zeros(img.shape, np.uint8)
            cv2.drawContours(mask, contours, i, (255, 255, 255), thickness=cv2.FILLED)
            out = cv2.bitwise_not(cv2.subtract(mask, res))[y:y+h, x:x+w]
            pred = self.classifier.predict(out) if self.classifier else None
            extracted.append(((x,y,w,h),pred))
        return extracted
