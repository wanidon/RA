import sys, os
#
from utils import *

gpdir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(gpdir)

from data_structures import Memory
m1 = Memory()
m1.mstore(BitVecVal256(4),BitVec256('x'))
m1.mstore(BitVecVal256(0x40), BitVecVal256(0x60))
print(m1.mload(BitVecVal256(4)))
print(m1.mload(BitVecVal256(5)))
print(m1.mload(BitVecVal256(0x3f)))
cut = m1.mload(BitVecVal256(0x50))
print(cut, cut.size())

m1.mstore8(BitVecVal256(0x40),BitVecVal256(0xff))
print(hex(m1.mload(BitVecVal256(0x40)).as_long()))
m1.show_data()

m2 = m1.duplicate(1)
m2.show_data()
m2.mstore8(BitVecVal256(0x71), BitVecVal256(0xfd))
m2.show_data()
