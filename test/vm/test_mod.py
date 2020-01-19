import sys, os
from z3 import simplify
from utils import *
from vm import VM
from data_structures import WorldState
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))


world_state = WorldState()

bytecode = '601060120600'

addr = world_state.add_account(bytecode)
print(addr)
vm = VM(world_state)
vm.init_state(addr)

vm.run()

vm.show_vm_state()
name,cfg = vm.cfmanager.gen_CFG()
print(cfg)


with open(name + '.dot', 'w') as f:
    f.write(cfg)


