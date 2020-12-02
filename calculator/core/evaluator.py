'''
@author: Hosung Lee
@date: December 2 2020
@description: Evaluator class
'''

from sympy.parsing.sympy_parser import parse_expr
from sympy.core.numbers import Float, ComplexInfinity
from calculator.utils.pipeline import Pipe

class Evaluator(Pipe):
    def __init__(self):
        pass

    def exec(self, arg=None):
        if arg:
            return Evaluator.evaluate(arg)
        return None
    
    @staticmethod
    def evaluate(string):
        string = string.replace("times", "*")
        string = string.replace("div", "/")
        converted = string
        if len(converted) == 0:
            return ""
        if converted[-1] == "=":
            converted = converted[0:len(converted)-1]
        converted = converted.replace("=", "==")
        converted = converted.replace(")(", ")*(")
        converted = converted.replace("^", "**")
        
        try:
            parsed = parse_expr(converted)

            evaluated = parsed.evalf() if not isinstance(parsed, bool) else parsed
            if type(evaluated) == Float:
                result = "%g"%(evaluated)
            elif type(evaluated) == ComplexInfinity:
                result = "div/0!"
            else:
                result = evaluated
            return string, result
        except SyntaxError as e:
            return string, "?"
        except TypeError as e:
            return string, "?"
        except Exception as e:
            return string, "?"
