# -*- coding: utf-8 -*-
import argparse
from os import listdir
from os.path import isdir, basename, isfile, join

if __name__ == "__main__":

    parser = argparse.ArgumentParser(description='Process some integers.')
    parser.add_argument('-t', metavar='test image path',help='testing image on given path')
    parser.add_argument('-m', metavar='model path', help='set classifier model specified on given path')

    args = parser.parse_args()

    print("loading modules...")
    import os
    os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'
    from app import CalculatorApplication
    from Calculator import Calculator

    calculator = Calculator(modelPath=args.m)
    if args.t:
        testpath = args.t
        imfiles = [testpath]

        if isdir(testpath):
            imfiles = [join(testpath, f) for f in listdir(testpath) if isfile(join(testpath, f))]
            print(imfiles)

        for imfile in imfiles:
            expr, res = calculator.exec(imfile)
            print(f"[{basename(imfile)}] Expression: {expr}\tResult: {res}")
            
    else:
        calculatorApp = CalculatorApplication(calculator)
        calculatorApp.run()
