class Symbol:
    classes = ['(',
        ')',
        '+',
        '-',
        '0',
        '1',
        '2',
        '3',
        '4',
        '5',
        '6',
        '7',
        '8',
        '9',
        '=',
        #'cos',
        'div',
        #'log',
        #'sin',
        'sqrt',
        #'tan',
        'times']

if __name__ == "__main__":
    import os
    for s in Symbol.classes:
        datapath = os.path.join(".","testdata",s)
        os.makedirs(datapath)
        print(datapath)