import cv2
import numpy as np
from PIL import Image

def extract(img, predictor):
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
        pred = predictor(out)
        extracted.append(((x,y,w,h),pred))
    return extracted