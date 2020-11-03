# -*- coding: utf-8 -*-
from gui import init_gui, run_gui
from model import Model
from predictor import predict
from extractor import extract
from segmentation import parse
from evaluator import evaluate

if __name__ == "__main__":
    calculatorModel = Model()
    calculatorModel.setPredictor(predict)
    calculatorModel.setExtractor(extract)
    calculatorModel.setParser(parse)
    calculatorModel.setEvaluator(evaluate)

    app, window = init_gui()
    window.setEvaluator(calculatorModel.evaluateFromSource)
    run_gui(app, window)