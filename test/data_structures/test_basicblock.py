import sys, os
from z3 import simplify, Solver, solve
from utils import *
from data_structures import *
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))


global pc
pc = -1
def gen_pc():
    global pc
    pc += 2
    return pc

accountnum = 0
print('test for mnemonics')
b1 = BasicBlock(account_number=0, block_number=0)
b1.add_mnemonic(gen_pc(), 'ADD')
b1.add_mnemonic(gen_pc(), 'PUSH1 ff')
print(b1.get_mnemonic())
b2 = b1.duplicate(accountnum,gen_pc() )
print(b2.get_mnemonic())
b2.add_mnemonic(gen_pc(), 'hoge')
print(b1.get_mnemonic())
print(b2.get_mnemonic())

print('test for call stack')
b1.push_call_stack(b2)
b1.show_call_stack()
b2.show_call_stack()
b1.pop_call_stack()
b1.show_call_stack()
b2.show_call_stack()


print('test for dfs stack')
b3 = b2.duplicate(accountnum, gen_pc())
b3.push_dfs_stack(b2)
b2.show_dfs_stack()
b3.show_dfs_stack()
b3.pop_dfs_stack()
b3.show_dfs_stack()


print('test for path condition')
b1.add_constraint_to_path_condition(BitVec256('x') < BitVecVal256(300))
solve(b1.get_path_condition())

b4 = b1.duplicate(accountnum, gen_pc())
b4.add_constraint_to_path_condition(BitVec256('x') < BitVecVal256(290))
b4.add_constraint_to_path_condition(BitVec256('x') > 40)
print(simplify(b4.get_path_condition()))
solve(b4.get_path_condition())

print(b1.extract_data())
print(b2.extract_data())
print(b3.extract_data())
print(b4.extract_data())