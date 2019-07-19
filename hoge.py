from z3 import *
x1 = BitVec('y',256)
x2 = BitVec('x2',256)
# solve(x1 > x2)
from z3 import Solver
s = Solver()
# s.add(x1 == 20)
# s.add(x2 == 30)
# r = s.check()
def hoge(fuga:BitVecVal):
    return fuga
print(hoge(BitVec('yyyyy',123)))
s.add(x1==20)
s.add(x2==x1)
print(s.push())
s.add(x2==30)
r = s.check()
if r == sat:
    m = s.model()
    print(m)
else:
    print(r)
s.pop()
r = s.check()
if r == sat:
    m = s.model()
    print(m)
else: print(r)
# solve(x1==20,x2==30)
p = Bool('p')
q = Bool('q')
r = Bool('r')
# p = q | q & r
print(simplify(Or(p,(And(p,q)))))
solve(p == Or(q,(And(q,r))), p==True,q==False)

print()

x = BitVecVal(678,256)
xname = str(x)
print(xname,type(xname))