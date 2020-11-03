class Model:
    def __init__(self):
        self.predictor = None
        self.extractor = None
        self.parser = None
        self.evaluator = None
    
    def setPredictor(self, predictor):
        self.predictor = predictor
    
    def setExtractor(self, extractor):
        self.extractor = extractor
    
    def setParser(self, parser):
        self.parser = parser
    
    def setEvaluator(self, evaluator):
        self.evaluator = evaluator
    
    def evaluateFromSource(self, src):
        extracted = self.extractor(src, self.predictor)
        parsed = self.parser(extracted)
        evaluated = self.evaluator(parsed)
        return parsed, evaluated