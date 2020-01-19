import sys, os
from z3 import simplify
from utils import *
from data_structures import *
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))


code = 'abcdef0123456789'
account_num = 0
a = Account(code,account_num)
print(a.code)
print(a.codesize())
print(a.account_num)
print(a.__balance)
