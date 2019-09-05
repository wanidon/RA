import sys, os
from z3 import simplify
from utils import *
from data_structures import *
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

manager = CfgManager('')

account_number = 0
block_number = 0

b1 = BasicBlock(account_number, block_number)
block_number += 1
b1.add_mnemonic(2, 'HOGE')
b1.add_mnemonic(2, 'HOGE2')
b1.add_mnemonic(2, 'HOGE3')
b1.set_jumpdest(0x1e)

b2 = b1.inherit(block_number)
block_number += 1
b2.add_mnemonic(2, 'FUGA')

b3 = b1.inherit(block_number,jflag=True)
block_number += 1
b3.add_mnemonic(2, 'HOGEFUGA')

manager.add_basic_block(b1)
manager.add_basic_block(b2)
manager.add_basic_block(b3)
manager.add_edge(b1, b2)
manager.add_edge(b1, b3)
print(manager.get_dest_blocks(b1))
name, cfg = manager.gen_CFG()
print(name)
print(cfg)
with open(name + '.dot', 'w') as f:
    f.write(cfg)


