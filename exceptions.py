class RuntimeErorr(Exception):
    __str__ = lambda self: 'Runtime error.'

class DevelopmentErorr(Exception):
    def __init__(self, msg=''):
        if len(msg) != 0:
            msg += ' '
        self.msg = msg
    __str__ = lambda self: 'Implementation or design error. ' + self.msg

class NotBitVecRef256Erorr(DevelopmentErorr):
    __str__ = lambda self: super().__str__() + 'The given object is not 256bit-BitVector.'

class EVMbytecodeError(DevelopmentErorr):
    __str__ = lambda self: super().__str__() + 'Or, the given EVM byte code may be incorrect.'
