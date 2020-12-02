'''
@author: Hosung Lee
@date: December 2 2020
@description: Classifier class
'''

from calculator.utils.imtool import convertImage
from calculator.utils.pipeline import Pipe
from calculator.network.symbols import Symbols
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
        return f"{Symbols.classes[ind]}"
