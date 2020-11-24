from imtool import convertImage
from symbol import Symbol
from Pipeline import Pipe
import numpy as np

class Classifier(Pipe):
    def __init__(self, network):
        self.threshold = 0.7
        self.network = network
    
    def exec(self, arg=None):
        if arg:
            return self.predict(arg)
        return None

    def predict(self, img):
        arr = convertImage(img)
        prd = self.network.predict(np.array([arr])/255)
        ind = np.argmax(prd)
        if prd[0][ind] < self.threshold:
            return "?"
        return f"{Symbol.classes[ind]}"