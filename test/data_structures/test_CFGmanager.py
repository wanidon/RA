import sys, os
from z3 import simplify
from utils import *
from data_structures import *
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

manager = CfgManager('')

account_number = 0
block_number = 0

b1 = BasicBlock(account_number, block_number)

manager.set_procesisng_block(b1)

manager.add_mnemonic('HOGE')
manager.processing_block.__machine_state.pc += 2
manager.add_mnemonic('HOGE2 84')
manager.processing_block.__machine_state.pc += 4

manager.set_jump_dest(0x1e)


manager.inherit_from_processing_block()
manager.add_mnemonic('FUGA')
manager.processing_block.__machine_state.pc += 2
manager.add_mnemonic('FUGA2 7e')
manager.processing_block.__machine_state.pc += 4

# TODO manager.rollback()
manager.add_mnemonic('FOO')
manager.processing_block.__machine_state.pc += 2
manager.add_mnemonic('BAR')
manager.processing_block.__machine_state.pc += 2


print(manager.get_dest_blocks(b1))
name, cfg = manager.gen_CFG()
print(name)
print(cfg)

with open(name + '.dot', 'w') as f:
    f.write(cfg)
manager.show_all()


