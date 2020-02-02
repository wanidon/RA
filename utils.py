from z3 import BitVecRef, BitVecNumRef, BitVec, BitVecVal, BitVecVal, BV2Int, simplify, If
from exceptions import NotBitVecRef256Erorr, NotBitVecNumRef256Erorr
from math import copysign
from sys import stderr

def BitVec256(name) -> BitVecRef:
    return BitVec(name,256)

def BitVecVal256(val) -> BitVecRef:
    return BitVecVal(val, 256)

def zero8bit()-> BitVecRef:
    return BitVecVal(0,8)

def checkBitVecRef256(word):
    if isinstance(word, BitVecRef) and word.size() == 256:
        return word
    else:
        raise NotBitVecRef256Erorr()

def checkBitVecNumRef256(word):
    if isinstance(word, BitVecNumRef) and word.size() == 256:
        return word
    else:
        raise NotBitVecNumRef256Erorr()

def sign(x):
    checkBitVecNumRef256(x)
    return copysign(1, x.as_signed_long())

def test_checkBitVecRef256():
    from z3 import BitVec, BitVecVal
    print(checkBitVecRef256(BitVecVal(111,256)))
    print(checkBitVecRef256(BitVec('x',256)))
    #print(isBitVecRef256(34))a
    print(checkBitVecRef256(BitVec('y',128)))
    print('hoge')

def BitVecOne256():
    return BitVecVal256(1)

def BitVecZero256():
    return BitVecVal256(0)

DEBUG = True
def pdbg(*somthing):
    if DEBUG: print(*somthing)


def bv_to_signed_int(x):
    return simplify(If(x < 0, BV2Int(x) - 2 ** x.size(), BV2Int(x)))

def dbgredmsg(*something):
    stderr.write(' '.join([str(d) for d in something])+'\n')




if __name__ == '__main__':
    test_checkBitVecRef256()
