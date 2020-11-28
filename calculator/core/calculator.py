# -*- coding: utf-8 -*-
from .classifier import Classifier
from .extractor import Extractor
from .parser import Parser
from .evaluator import Evaluator
from calculator.utils.pipeline import Pipeline

class CalculatorCore(Pipeline):
    def __init__(self, network, extractor=None, classifier=None, parser=None, evaluator=None):
        self.network = network
        self.classifier = classifier if classifier else Classifier(self.network)
        self.extractor = extractor if extractor else Extractor(self.classifier)
        self.parser = parser if parser else Parser()
        self.evaluator = evaluator if evaluator else Evaluator()

        super().__init__(self.extractor, self.parser, self.evaluator)
    
    def calculate(self, img):
        return self.exec(img)

def createCalculator(network):
    return CalculatorCore(network)
