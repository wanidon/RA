from z3 import *
from exceptions import NotBitVecRef256Erorr, NotBitVecNumRef256Erorr
from math import copysign
from sys import stderr
import time_measurement
from time import perf_counter
import os


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

def reset_time():
    time_measurement.exec_time[os.getpid()] = perf_counter()
    time_measurement.solving_time[os.getpid()] = 0

def get_time():
    return perf_counter() - time_measurement.exec_time[os.getpid()], time_measurement.solving_time[os.getpid()]

def solve_and_time(condition, solver=None):
    s = Solver() if solver is None else solver
    s.add(condition)
    t = perf_counter()
    r = s.check()
    print(time_measurement.solving_time)
    time_measurement.solving_time[os.getpid()] += perf_counter() - t
    #
    return r == sat

def get_model_and_time(condition, solver=None):
    s = Solver() if solver is None else solver
    s.add(condition)
    t = perf_counter()
    r = s.check()
    time_measurement.solving_time[os.getpid()] += perf_counter() - t
    return s.model() if r == sat else False

if __name__ == '__main__':
    test_checkBitVecRef256()
