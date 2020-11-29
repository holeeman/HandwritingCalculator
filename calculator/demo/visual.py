from calculator.core.segmentation import Token, Lexer, is_exp, is_sub, get_group_ybox, segment

BOX_RED, BOX_GREEN, BOX_BLUE = (0, 0, 255), (0, 255, 0), (255, 0, 0)

def drawRect(img, rect, color):
    x, y, w, h = rect
    cv2.rectangle(img, (x,y), (x+w,y+h), color)

def drawGroupRect(img, group, color, width=None):
    if len(group) == 0:
        return
    minx, miny, maxx, maxy = (float("inf"),float("inf"),-1,-1)
    for t in group:
        x, y, w, h = t.rect
        if x < minx:
            minx = x
        if y < miny:
            miny = y
        if x+w > maxx:
            maxx = x+w
        if y+h > maxy:
            maxy = y+h
    cv2.rectangle(img, (minx, miny), (maxx, maxy), color, thickness=width)

def debugRect(group, color=(255, 0, 0), width=None):
    drawGroupRect(im, group, color, width)
    cv2.imshow("im", im)
    cv2.waitKey(wait)

    
def hss(tokens):
    #tokens = sorted(tokens, key= lambda x: x.x)
    groups = []
    group = []
    xbound = -1
    if len(tokens) == 1:
        debugRect(tokens, BOX_GREEN, 2)
        return tokens[0].symbol
    if len(tokens) > 0 and tokens[0].symbol == 'sqrt':
        return parse_sqrt(tokens)
    for t in tokens:
        if len(group) > 0 and (t.x > xbound or group[0].symbol not in ['-', 'sqrt']):
            groups.append(group)
            group = []
        group.append(t)
        xbound = max(t.x + t.w, xbound)
    if len(group) > 0:
        groups.append(group)
        group = []

    for g in groups:
        debugRect(g, BOX_RED, 2)

    return parse_exp(groups)

def vss(tokens):
    if len(tokens) == 1:
        debugRect(tokens, BOX_GREEN, 2)
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
    
    debugRect(bottom, BOX_BLUE, 2)
    debugRect(top, BOX_BLUE, 2)
    
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
        if len(groups[i]) == 1 and groups[i][0].symbol_type not in [Token.Digit, Token.Group]:
            continue
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

def vevaluate(img, _wait=100, _timeout=500):
    import os
    import sys
    os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'
    from ..network.models import loadClassifierModel
    from calculator.core.extractor import Extractor
    from calculator.core.classifier import Classifier
    from calculator.core.evaluator import Evaluator
    global cv2
    import cv2

    extractor = Extractor(Classifier(loadClassifierModel("recognition_model")))
    extracted = extractor.extract(img)
    global im, wait, timeout
    im = cv2.imread(img)
    wait = _wait
    timeout = _timeout

    _tokens = Lexer.lex(extracted)
    _tokens = sorted(_tokens, key=lambda x: (x.x, x.y))
    cv2.imshow("im", im)
    cv2.waitKey(wait)
    string = hss(_tokens)
    a, b = Evaluator.evaluate(string)
    cv2.putText(im, a, (20, im.shape[0]-30), cv2.cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), thickness=1)
    cv2.imshow("im", im)
    cv2.waitKey(timeout)
    return a, b

if __name__ == '__main__':
    print("loading modules...")
    import os
    import sys
    os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'
    from ..network.models import loadClassifierModel
    from calculator.core.extractor import Extractor
    from calculator.core.classifier import Classifier
    from calculator.core.evaluator import Evaluator
    import cv2
    
    extractor = Extractor(Classifier(loadClassifierModel("recognition_model")))
    if len(sys.argv) > 1:
        sample = sys.argv[1]
    else:
        sample = "samples/sample13.PNG"
    vevaluate(sample)