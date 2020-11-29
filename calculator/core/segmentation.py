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
    #tokens = sorted(tokens, key= lambda x: x.x)
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
