from collections import deque
from copy import deepcopy
from z3 import BitVec, BitVecVal, Concat, Extract, simplify

WORDBITSIZE = 256
WORDBYTESIZE = WORDBITSIZE // 8


class Stack():
    # def __init__(self, blockNumber=0, stdata=deque(), numStackVar=0):
    def __init__(self, blockNumber=0, stdata_and_numStackVar=(deque(), 0)):
        # blockNumber will be VM object's member
        self.blockNumber = blockNumber
        self.stdata = stdata_and_numStackVar[0]
        self.size = lambda: len(self.stdata)
        self.numStackVar = stdata_and_numStackVar[1]

    def generateCopy(self):
        return deepcopy(self.stdata), self.numStackVar

    def generateStackVar(self):
        self.numStackVar += 1
        return BitVec(
            'stackVar{}-{}'.format(self.blockNumber, self.numStackVar),
            256)

    def push(self, w):
        if self.size() < 1023:
            # w must be a 256bit-bitvec object
            self.stdata.append(w)
        else:
            # TODO stack limit reached 1024
            pass

    def pop(self):
        if self.size() >= 1:
            return self.stdata.pop()
        else:
            # generate a symbolic variable
            return self.generateStackVar()

    def swapx(self, x):
        if x < 1 or 16 < x:
            # TODO error due to misshandle opcode
            pass

        if x + 1 > self.size():
            for _ in range(x + 1 - self.size()):
                self.stdata.appendleft(self.generateStackVar)

        a = self.stdata[self.size() - 1]
        self.stdata[self.size() - 1] = self.stdata[self.size() - 1 - x]
        self.stdata[self.size() - 1 - x] = a

    def dupx(self, x):
        if x < 1 or 16 < x:
            # TODO error due to misshandle opcode
            pass

        if x > self.size():
            for _ in range(x - self.size()):
                self.stdata.appendleft(self.generateStackVar)

        self.stdata.append(self.stdata[self.size() - x])


class Memory():
    def __init__(self, blockNumber=0, memdata=[], numMemoryVar=0):
        # blockNumber will be VM object's member
        self.blockNumber = blockNumber
        self.memdata = memdata
        self.size = lambda: len(self.memdata)
        self.numMemoryVar = numMemoryVar

    def generateMemoryVar(self):
        self.numMemoryVar += 1
        return BitVec(
            'memoryVar{}-{}'.format(self.blockNumber, self.numMemoryVar),
            256)

    def mstore(self, offset, value):
        if offset + WORDBYTESIZE > self.size():
            d = offset + WORDBYTESIZE - self.size()
            self.memdata.extend([BitVecVal(0, 8) for _ in range(d)])

        for i in range(WORDBYTESIZE):
            self.memdata[offset+i] = Extract(i*8+7, i*8, value)

    def mload(self, offset):
        if offset + WORDBYTESIZE > self.size():
            # ~ index out of bounds ~
            # generate a symblolic variable
            newmemvar = self.generateMemoryVar()
            self.mstore(offset, newmemvar)
            return newmemvar

        elif offset < 0:
            # TODO  index out of bounds
            pass
        else:
            return simplify(
                Concat(self.memdata[offset+WORDBYTESIZE:offset:-1]))

    def msize(self):
        return self.memsize

# TODO storage
# TODO return data
# TODO call data

if __name__ == '__main__':
    m = Memory()
    m.mstore(0,BitVec("hoge",256))
    print(m.mload(0))
    print(m.mload(45))
    print(m.memdata)

    s = Stack()
    t = BitVecVal(100+ 2**1024-1,256)
    print(t)
    s.push(t)
    print(s.pop())
    print(s.pop())
    s.push(BitVecVal(1,256))
    s.push(BitVecVal(2,256))
    s.push(BitVec("hoge",256))
    s.push(BitVecVal(4,256))
    s.swapx(1)
    s.dupx(1)
    s.dupx(5)
    s.swapx(4)
    import sys
    for i in range(s.size()):
        sys.stdout.write(str(s.stdata[i]))
        sys.stdout.write(' ')

    s2 = Stack(1,(s.generateCopy()) )
    for i in range(s2.size()):
        sys.stdout.write('i={} '.format(i))
        sys.stdout.write(str(simplify(s2.stdata[i] * BitVecVal(2,256) / BitVecVal(2,256))))
        print()



