class Pipe:
    def exec(self, arg=None):
        ...

class Pipeline:
    def __init__(self, *args):
        self.pipes = list(args)
    
    def add(self, pipe):
        self.pipes.append(pipe)
    
    def exec(self, arg=None):
        for pipe in self.pipes:
            arg = pipe.exec() if arg is None else pipe.exec(arg)
        return arg
