class Token:
    Digit = 'd'
    Operator = 'o'
    Group = 'p'
    Function = 'f'

    def __init__(self, symbol_tuple, symbol_type):
        self.rect, self.symbol = symbol_tuple
        self.x, self.y, self.w, self.h = self.rect
        self.symbol_type = symbol_type

    def gtype(self):
        return self.symbol_type
    
    def __repr__(self):
        return f"{self.symbol_type}(\'{self.symbol}\')"

class Lexer:
    @staticmethod
    def lex(extracted):
        tokens = []
        for st in extracted:
            _, s = st
            if s in ['(', ')']:
                tokens.append(Token(st, Token.Group))
            elif s in ['+', '-', 'div', 'times', '=']:
                tokens.append(Token(st, Token.Operator))
            elif s in ['0','1','2','3','4','5','6','7','8','9']:
                tokens.append(Token(st, Token.Digit))
            elif s in ['sqrt']:
                tokens.append(Token(st, Token.Function))
        return tokens

def print_rec(exp_tree):
    if(isinstance(exp_tree, list)):
        for t in exp_tree:
            print_rec(t)
        print()
        return
    print(f"{exp_tree}", end="  ")

def hss(tokens):
    tokens = sorted(tokens, key= lambda x: x.x)
    groups = []
    group = []
    xbound = -1
    if len(tokens) == 1:
        return tokens[0].symbol
    if len(tokens) > 0 and tokens[0].symbol == 'sqrt':
        return parse_sqrt(tokens)
    for t in tokens:
        if len(group) > 0 and (t.x > xbound or group[0].gtype() == Token.Digit):
            groups.append(group)
            group = []
        group.append(t)
        xbound = max(t.x + t.w, xbound)
    if len(group) > 0:
        groups.append(group)
        group = []
    return parse_exp(groups)

def vss(tokens):
    if len(tokens) == 1:
        return tokens[0].symbol
    frac_bar = [x for x in tokens if x.symbol == '-']
    if len(frac_bar) == 0:
        return hss(tokens)
    
    longest = max(frac_bar, key=lambda x:x.w)
    top, bottom = [], []
    for t in tokens:
        if t == longest:
            continue
        elif t.y > longest.y:
            bottom.append(t)
        else:
            top.append(t)
    if len(top) > 0 and len(bottom) > 0:
        return "".join(["(",hss(top),")","/","(",*hss(bottom),")"])
    elif len(frac_bar) == 2 and len(tokens) == 2:
        return "="
    else:
        parsed_top = ["(",hss(top),")"] if len(top) > 0 else ['?']
        parsed_bottom = ["(",hss(bottom),")"] if len(bottom) > 0 else ['?']
    return "".join(parsed_top+["/"]+parsed_bottom)

def parse_sqrt(tokens):
    sq = tokens[0]
    inner, outer = [], []
    for t in tokens[1:]:
        if t.x < sq.x + sq.w and t.x > sq.x:
            inner.append(t)
        else:
            outer.append(t)
    return "".join(['sqrt', '(', hss(inner) if len(inner) > 0 else '?', ')', hss(outer) if len(outer) else ''])

def parse_exp(groups):
    if len(groups) == 1:
        return vss(groups[0])
    group = []
    stack = []
    for i in range(len(groups)-1):
        group.append(vss(groups[i]))
        if is_exp(get_group_ybox(groups[i]), get_group_ybox(groups[i+1])):
            group.append("^(")
            stack.append("(")
        if is_sub(get_group_ybox(groups[i]), get_group_ybox(groups[i+1])):
            group.append(")")
            stack.pop()
    group.append(vss(groups[-1]))
    while len(stack) > 0:
        stack.pop()
        group.append(")")
    return "".join(group)

def is_exp(rect1, rect2, t1=0.1, t2=0.9):
    _, y1, _, h1 = rect1
    _, y2, _, h2 = rect2
    return y1 + t1 * h1 > y2 + t2 * h2

def is_sub(rect1, rect2, t1=0.9, t2=0.1):
    _, y1, _, h1 = rect1
    _, y2, _, h2 = rect2
    return y1 + t1 * h1 < y2 + t2 * h2

def get_group_ybox(group):
    mins, miny = None, float("inf")
    maxs, maxy = None, float("-inf")
    for token in group:
        if token.y < miny:
            mins, miny = token, token.y
        if token.y > maxy:
            maxs, maxy = token, token.y
    return (mins.x, mins.y, maxs.x - mins.x + maxs.w, maxs.y - mins.y + maxs.h)

def segment(extracted):
    _tokens = Lexer.lex(extracted)
    _tokens = sorted(_tokens, key=lambda x: (x.x, x.y))
    return hss(_tokens)

if __name__ == '__main__':
    # import os
    # os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'
    # from Extractor import Extractor
    # from Classifier import Classifier
    # from Network import Network

    # network = Network()
    # network.load("recognition_model")
    # extractor = Extractor(Classifier(network))
    # print(extractor.extract("samples/sample10.PNG"))

    extracted5 = [((354, 283, 71, 81), '5'), ((22, 226, 605, 45), '-'), ((134, 179, 44, 14), '-'), ((45, 144, 5, 96), '1'), ((213, 141, 67, 83), '3'), ((38, 102, 338, 23), '-'), ((423, 76, 64, 62), '+'), ((511, 65, 77, 96), '3'), ((213, 32, 6, 65), '1')]
    extracted7 = [((79, 166, 31, 48), '3'), ((171, 164, 34, 39), '+'), ((219, 159, 35, 44), '7'), ((112, 155, 36, 23), '2'), ((28, 
    139, 240, 79), 'sqrt'), ((485, 138, 29, 4), '-'), ((5, 123, 301, 8), '-'), ((486, 111, 25, 5), '-'), ((352, 106, 40, 38), '+'), ((406, 99, 42, 53), '2'), ((556, 92, 37, 75), '3'), ((143, 35, 32, 53), '+'), ((68, 33, 49, 77), '3'), ((224, 26, 5, 58), '1')]
    extracted8 = [((367, 160, 51, 59), '+'), ((34, 156, 117, 84), '2'), ((466, 132, 57, 92), '3'), ((599, 98, 36, 4), '-'), ((219, 97, 39, 49), '+'), ((137, 93, 54, 63), '2'), ((291, 87, 5, 58), '1'), ((541, 70, 38, 64), '3'), ((666, 65, 5, 61), '1')]
    extracted10 = [((292, 135, 35, 6), '-'), ((533, 109, 26, 46), '+'), ((141, 108, 59, 74), '2'), ((594, 101, 73, 63), '2'), ((402, 79, 6, 104), '1'), ((43, 43, 167, 167), 'sqrt')]
    segmented = segment(extracted10)

    print(segmented)
    