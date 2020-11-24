# -*- coding: utf-8 -*-
import argparse

if __name__ == "__main__":

    parser = argparse.ArgumentParser(description='Process some integers.')
    parser.add_argument('-t', metavar='test image path',help='testing image on given path')
    parser.add_argument('-m', metavar='model path', help='set classifier model specified on given path')
    args = parser.parse_args()
    from app import CalculatorApplication
    from Calculator import Calculator

    calculator = Calculator(modelPath=args.m)
    if args.t:
        testpath = args.t
        print(f"Testing image on {testpath}: ")
        expr, res = calculator.exec(testpath)
        print(f"Expression: {expr}\tResult: {res}")
    else:
        calculatorApp = CalculatorApplication(calculator)
        calculatorApp.run()
