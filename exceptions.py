class RuntimeErorr(Exception):
    __str__ = lambda self: 'Runtime error.'

class DevelopmentErorr(Exception):
    __str__ = lambda self: 'Implementation or design error.'

class NotBitVecRef256Erorr(DevelopmentErorr):
    def __init():
        super().__init__()
    __str__ = lambda self: super().__str__() + ' The given object is not 256bit-BitVector.'
