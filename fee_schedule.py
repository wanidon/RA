from collections import defaultdict
from data_structures import WorldState, MachineState, ExecutionEnvironment
W_ZERO = 'W_ZERO'



G_ZERO = 'G_ZERO'

mnemonic_to_instruction_subset = {
    'STOP': W_ZERO
}

instruction_subset_to_fee_name = {
    W_ZERO: G_ZERO
}

schedule = {
    G_ZERO:0
}

def mnemonic_to_fee(mnemonic:str):
    pass

# CCALL, CSELFDESTRUCT and CSSTORE
def c_call():
    pass

def c_selfdestruct():
    pass

def c_sstore():
    pass

#  the memory cost function
def c_mem():
    pass

# The general gas cost function
def c(world_state, machine_state, execution_environment):
    return 1
