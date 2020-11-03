from network import Network
from imtool import convertImage
from symbol import Symbol
import numpy as np
class PredictSetting:
    threshold = 0.7
    network = Network()

PredictSetting.network.load("recognition_model")

def predict(img):
    arr = convertImage(img)
    prd = PredictSetting.network.predict(np.array([arr])/255)
    ind = np.argmax(prd)
    if prd[0][ind] < PredictSetting.threshold:
        return "?"
    return f"{Symbol.classes[ind]}"