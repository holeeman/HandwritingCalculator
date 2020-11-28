import cv2
import numpy as np
from PIL import Image
from Pipeline import Pipe
from segmentation import *

class Parser(Pipe):
    def __init__(self):
        pass

    def exec(self, arg=None):
        if arg:
            return Parser.parse(arg)
        return None
    
    @staticmethod
    def parse(arr):
        if arr == 0:
            return ""
        return segment(arr)