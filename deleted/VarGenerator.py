from z3 import BitVec
class VarGenerator():
    def __init__(self):
        self.numMemoryVar = 0
        self.numStackVar = 0
        self.numStorageVar = 0

    def generateMemoryVar():
        self.numMemoryVar += 1
        return BitVec('memoryVar{}'.format(self.numMemoryVar),256)
        