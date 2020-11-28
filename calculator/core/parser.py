from calculator.utils.pipeline import Pipe
from calculator.core.segmentation import segment

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
