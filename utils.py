from z3 import BitVecRef

from exceptions import NotBitVecRef256Exception
def isBitVecRef256(word):
    if isinstance(word,BitVecRef) and word.size() == 256:
        return True
    else:
        raise NotBitVecRef256Exception()
        return False




def test_isBitVecRef256():
    from z3 import BitVec, BitVecVal
    print(isBitVecRef256(BitVecVal(111,256)))
    print(isBitVecRef256(BitVec('x',256)))
    #print(isBitVecRef256(34))a
    print(isBitVecRef256(BitVec('y',128)))
    print('hoge')
if __name__ == '__main__':
    test_isBitVecRef256()
