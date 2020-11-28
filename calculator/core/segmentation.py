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
            else:
                tokens.append(Token(st, '?'))
        return tokens

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
        if len(group) > 0 and (t.x > xbound or group[0].gtype() in [Token.Digit, Token.Group]):
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
    if len(tokens) > 0 and tokens[0].symbol == 'sqrt':
        return parse_sqrt(tokens)
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
    # print("top", top)
    # print("bottom", bottom)
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
        # print('g', group)
        if is_exp(get_group_ybox(groups[i]), get_group_ybox(groups[i+1])):
            group.append("^(")
            stack.append("(")
        if is_sub(get_group_ybox(groups[i]), get_group_ybox(groups[i+1])) and len(stack) > 0:
            group.append(")")
            # print(group)
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
    #
    # network = Network()
    # network.load("recognition_model")
    # extractor = Extractor(Classifier(network))
    # print(extractor.extract("samples/sample12.PNG"))


    extracted5 = [((354, 283, 71, 81), '5'), ((22, 226, 605, 45), '-'), ((134, 179, 44, 14), '-'), ((45, 144, 5, 96), '1'), ((213, 141, 67, 83), '3'), ((38, 102, 338, 23), '-'), ((423, 76, 64, 62), '+'), ((511, 65, 77, 96), '3'), ((213, 32, 6, 65), '1')]
    extracted7 = [((79, 166, 31, 48), '3'), ((171, 164, 34, 39), '+'), ((219, 159, 35, 44), '7'), ((112, 155, 36, 23), '2'), ((28, 
    139, 240, 79), 'sqrt'), ((485, 138, 29, 4), '-'), ((5, 123, 301, 8), '-'), ((486, 111, 25, 5), '-'), ((352, 106, 40, 38), '+'), ((406, 99, 42, 53), '2'), ((556, 92, 37, 75), '3'), ((143, 35, 32, 53), '+'), ((68, 33, 49, 77), '3'), ((224, 26, 5, 58), '1')]
    extracted8 = [((367, 160, 51, 59), '+'), ((34, 156, 117, 84), '2'), ((466, 132, 57, 92), '3'), ((599, 98, 36, 4), '-'), ((219, 97, 39, 49), '+'), ((137, 93, 54, 63), '2'), ((291, 87, 5, 58), '1'), ((541, 70, 38, 64), '3'), ((666, 65, 5, 61), '1')]
    extracted10 = [((292, 135, 35, 6), '-'), ((533, 109, 26, 46), '+'), ((141, 108, 59, 74), '2'), ((594, 101, 73, 63), '2'), ((402, 79, 6, 104), '1'), ((43, 43, 167, 167), 'sqrt')]
    extracted11 = [((245, 403, 42, 33), '2'), ((585, 394, 29, 5), '-'), ((233, 382, 69, 8), '-'), ((162, 378, 31, 31), '+'), ((86, 378, 48, 38), '2'), ((725, 377, 24, 33), '+'), ((412, 376, 37, 6), '-'), ((531, 373, 33, 52), '3'), ((637, 370, 42, 41), '2'), ((772, 367, 37, 49), '7'), ((679, 354, 23, 18), '2'), ((258, 342, 3, 31), '1'), ((210, 338, 20, 109), '('), ((470, 335, 399, 97), 'sqrt'), ((317, 335, 15, 102), ')'), ((344, 328, 24, 22), '2'), ((6, 305, 930, 9), '-'), ((543, 261, 21, 31), '3'), ((533, 249, 40, 5), '-'), ((64, 237, 48, 43), '2'), ((130, 234, 3, 44), '1'), ((152, 213, 28, 27), '2'), ((544, 207, 24, 30), '2'), ((194, 204, 22, 76), ')'), ((38, 203, 20, 91), '('), ((508, 189, 85, 4), '-'), ((412, 169, 41, 47), '+'), ((252, 167, 29, 28), 'times'), ((297, 165, 3, 33), '1'), ((222, 165, 19, 35), '3'), ((536, 147, 21, 27), '2'), ((25, 138, 292, 6), '-'), ((526, 132, 41, 6), '-'), ((89, 95, 18, 4), '-'), ((606, 86, 27, 204), ')'), ((226, 84, 24, 25), 'times'), ((538, 83, 23, 38), '5'), ((267, 79, 36, 39), '2'), ((124, 79, 22, 44), '7'), ((479, 77, 30, 215), '('), ((166, 77, 4, 46), 
'1'), ((39, 76, 31, 49), '3'), ((739, 55, 33, 28), '2'), ((687, 53, 22, 31), 'div'), ((644, 52, 24, 30), '7'), ((181, 48, 29, 26), '2')]
    need_debug = [((245, 403, 42, 33), '2'), ((585, 394, 29, 5), '-'), ((233, 382, 69, 8), '-'), ((162, 378, 31, 31), '+'), ((86, 378, 48, 38), '2'), ((725, 377, 24, 33), '+'), ((412, 376, 37, 6), '-'), ((531, 373, 33, 52), '3'), ((637, 370, 42, 41), '2'), ((772, 367, 37, 49), '7'), ((679, 354, 23, 18), '2'), ((258, 342, 3, 31), '1'), ((210, 338, 20, 109), '('), ((470, 335, 399, 97), 'sqrt'), ((317, 335, 15, 102), ')'), ((332, 319, 25, 19), '2'), ((6, 305, 930, 9), '-'), ((543, 261, 21, 31), '3'), ((533, 249, 40, 5), '-'), ((64, 237, 48, 43), '2'), ((130, 234, 3, 44), '1'), ((152, 213, 28, 27), '2'), ((544, 207, 24, 30), '2'), ((194, 204, 22, 76), ')'), ((38, 203, 20, 91), '('), ((508, 189, 85, 4), '-'), ((412, 169, 41, 47), '+'), ((252, 167, 29, 28), 'times'), ((297, 165, 3, 33), '1'), ((222, 165, 19, 35), '3'), ((536, 147, 21, 27), '2'), ((25, 138, 292, 6), '-'), ((526, 132, 41, 6), '-'), ((89, 95, 18, 4), '-'), ((606, 86, 27, 204), ')'), ((226, 84, 24, 25), 'times'), ((538, 83, 23, 38), '5'), ((267, 79, 36, 39), '2'), ((124, 79, 22, 44), '7'), ((479, 77, 30, 215), '('), ((166, 77, 4, 46), 
'1'), ((39, 76, 31, 49), '3'), ((739, 55, 33, 28), '2'), ((687, 53, 22, 31), 'div'), ((644, 52, 24, 30), '7'), ((181, 48, 29, 26), '2')]
    sample12 = [((226, 211, 44, 6), '-'), ((191, 200, 9, 38), '1'), ((82, 198, 28, 4), '-'), ((287, 193, 16, 42), '1'), ((134, 164, 209, 83), 'sqrt'), ((49, 132, 290, 16), '-'), ((203, 29, 6, 56), '1')]
    import cv2
    # print(sorted(Lexer.lex(extracted11), key=lambda x: (x.x, x.y)))
    # im = cv2.imread("samples/sample11.png")
    # for e in extracted11:
    #     rect, s = e
    #     x, y, w, h = rect
    #     cv2.rectangle(im, (x,y), (x+w,y+h), (255, 0, 0))
    #     cv2.putText(im, s, (x, y), cv2.FONT_HERSHEY_COMPLEX, 1, (0,0,255), 2)
    # cv2.imshow("im", im)
    # cv2.waitKey(0)
    #need_debug = [((39, 76, 31, 49), '?')]
    #segmented = segment(sample12)
    _tokens = Lexer.lex(need_debug)
    _tokens = sorted(_tokens, key=lambda x: (x.x, x.y))
    r = hss(_tokens)
    print(r)
    