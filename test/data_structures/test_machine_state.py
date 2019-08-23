import sys, os
from z3 import simplify
from utils import *
from data_structures import Machine_state

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

µ = Machine_state()
mem = µ.get_memory()
stack = µ.get_stack()
storage = µ.get_storage()
mem.show_data()
stack.show_data()
storage.show_data()