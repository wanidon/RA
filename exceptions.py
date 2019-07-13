class RuntimeException(Exception):
    # __repr__ = lambda: 'runtime error'
    # __str__ = lambda: 'runtime error'
    pass

class NotBitVecRef256Exception(RuntimeException):
    __repr__ = lambda self: 'The given object is not 256bit-BitVector.'
    __str__ = __repr__
    #'The given object is not 256bit-BitVector.'
