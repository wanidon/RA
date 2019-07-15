import sys,os

gpdir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(gpdir)

from z3 import *

from data_structures import Stack
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
    sys.stdout.write(str(s.stackdata[i]))
    sys.stdout.write(' ')

s2 = s.duplicate(1)
for i in range(s2.size()):
    sys.stdout.write('i={} '.format(i))
    sys.stdout.write(str(simplify(s2.stackdata[i] * BitVecVal(2, 256) / BitVecVal(2, 256))))
    print()
s.push(7)