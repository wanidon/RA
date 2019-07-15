from z3 import BitVecRef

from exceptions import NotBitVecRef256Erorr

def checkBitVecRef256(word):
    if isinstance(word,BitVecRef) and word.size() == 256:
        return word
    else:
        raise NotBitVecRef256Erorr()




def test_checkBitVecRef256():
    from z3 import BitVec, BitVecVal
    print(checkBitVecRef256(BitVecVal(111,256)))
    print(checkBitVecRef256(BitVec('x',256)))
    #print(isBitVecRef256(34))a
    print(checkBitVecRef256(BitVec('y',128)))
    print('hoge')
if __name__ == '__main__':
    test_checkBitVecRef256()
