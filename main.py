'''
@author: Hosung Lee
@date: December 2 2020
@description: Main program, uses calculator package.
'''

import argparse
from os import listdir
from os.path import isdir, basename, isfile, join

if __name__ == "__main__":

    parser = argparse.ArgumentParser(description='Recognize and evaluates handwritten math expressions.')
    parser.add_argument('-t', metavar='test image path',help='testing image on given path')
    parser.add_argument('-m', metavar='model path', help='set classifier model specified on given path')
    parser.add_argument('--no-graphics', action='store_const', const=True, help='doesn\'t display graphics when running test file(s)')

    args = parser.parse_args()

    if args.no_graphics and not args.t:
        parser.error("--no-graphics flag requires -t flag")
        print("--no-graphics flag")

    print("loading modules...")

    import os
    os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'
    from calculator.ui.gui import GUICalculatorApplication
    from calculator.core.calculator import createCalculator
    from calculator.network.models import loadClassifierModel
    from calculator.demo.visual import vevaluate
    modelPath = args.m if args.m else "recognition_model"

    calculator = createCalculator(loadClassifierModel(modelPath))

    if args.t:
        testpath = args.t
        imfiles = [testpath]

        if isdir(testpath):
            imfiles = [join(testpath, f) for f in listdir(testpath) if isfile(join(testpath, f))]

        for imfile in imfiles:
            p, e = calculator.calculate(imfile) if args.no_graphics else vevaluate(imfile, _wait=50, _timeout=50)
            print(f" ====== {basename(imfile)} ======")
            print("* Equation: ")
            print(f" {p}")
            print()
            print("* Evaluation: ")
            print(f" {e}")
            print()
            
    else:
        calculatorApp = GUICalculatorApplication(True, False)
        calculatorApp.connect(calculator.calculate)
        calculatorApp.run()