# -*- coding: utf-8 -*-
from app import CalculatorApplication
from Calculator import Calculator
if __name__ == "__main__":
    calculator = Calculator()
    calculatorApp = CalculatorApplication(calculator)
    calculatorApp.run()