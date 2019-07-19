#import sys, os
from z3 import *
from exceptions import NotBitVecRef256Erorr

gpdir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(gpdir)

raise NotBitVecRef256Erorr("hoge.")
raise NotBitVecRef256Erorr()