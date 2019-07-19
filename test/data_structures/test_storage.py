from z3 import *
from utils import *
from data_structures import Storage
gpdir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(gpdir)


s1 = Storage()
s1.sstore(BitVecVal(3,256), BitVecVal(4,256))
s1.sstore(BitVec256('x'), BitVecVal256(98))
print(s1.sload(BitVec256('x')))
print(s1.sload(BitVecVal256(67)))
s1.show_data()

s2 = s1.duplicate(1)
s2.sstore(BitVecVal256(3),BitVecVal256(8989))
s2.sstore(BitVec256('y'), BitVec256('asdfj;k'))
s2.show_data()
print()
s1.show_data()