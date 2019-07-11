from z3 import *
x1 = BitVec('y',256)
x2 = BitVec('x2',256)
from z3 import Solver
s = Solver
# s.add(x1 == 20)
# s.add(x2 == 30)
# r = s.check()
solve(x1==20,x2==30)
print()