import sys, os
from z3 import simplify
from utils import *
from data_structures import *
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
manager = CFGmanager()