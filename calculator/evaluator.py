from sympy.parsing.sympy_parser import parse_expr
from Pipeline import Pipe

class Evaluator(Pipe):
    def __init__(self):
        pass

    def exec(self, arg=None):
        if arg:
            return self.evaluate(arg)
        return None
    
    def evaluate(self, string):
        if len(string) == 0:
            return ""
        if string[-1] == "=":
            string = string[0:len(string)-1]
        string = string.replace("=", "==")
        string = string.replace("times", "*")
        string = string.replace("div", "/")
        string = string.replace(")(", ")*(")
        
        try:
            evaluated = parse_expr(string).evalf()
            return string, "%g"%(evaluated)
        except SyntaxError:
            return string, "?"
        except TypeError:
            return string, "?"
        except:
            return string, "?"