# -*- coding: utf-8 -*-
from Classifier import Classifier
from Extractor import Extractor
from Parser import Parser
from Evaluator import Evaluator
from Pipeline import Pipeline
from Network import Network

class Calculator(Pipeline):
    def __init__(self, modelPath=None, network=None, extractor=None, classifier=None, parser=None, evaluator=None):
        if network:
            self.network = network
        else:
            self.network = Network()
            self.network.load(modelPath if modelPath else "recognition_model")
        
        self.classifier = classifier if classifier else Classifier(self.network)
        self.extractor = extractor if extractor else Extractor(self.classifier)
        self.parser = parser if parser else Parser()
        self.evaluator = evaluator if evaluator else Evaluator()

        super().__init__(self.extractor, self.parser, self.evaluator)
