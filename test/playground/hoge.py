from z3 import *
p = BitVecVal(8,256)
q = BitVec('x',256)
P = p > q
Q = p
Or(p,q)