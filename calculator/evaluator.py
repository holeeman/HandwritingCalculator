from sympy.parsing.sympy_parser import parse_expr
def evaluate(string):
    if len(string) == 0:
        return ""
    if string[-1] == "=":
        string = string[0:len(string)-1]
    string = string.replace("=", "==")
    string = string.replace("times", "*")
    string = string.replace("div", "/")
    string = string.replace(")(", ")*(")
    
    try:
        return parse_expr(string)
    except SyntaxError:
        return "?"
    except TypeError:
        return "?"
    except:
        return "?"