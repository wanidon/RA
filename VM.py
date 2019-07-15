from data_strucutures import Stack,Memory,Storage,Returndata,Execution_environment,System_state,Machine_state
from web3 import Web3


class VM():
    def __init__(self,
    machine_state: Machine_state,
    system_state: System_state,
    exe_env: Execution_environment
    ):
        self.µ = machine_state
        self.σ = system_state
        self.I = Execution_environment
        self.stack = machine_state.stack
        self.memory = machine_statememory
        self.storage = storage
        self.returndata = returndata


    # 0s: Stop and Arithmetic Operations
    # 10s: Comparison & Bitwise Logic Operations
    # 20s: SHA3
    def sha3():
        offset = self.stack.pop()
        length = self.stack.pop()


    # 30s: Environmental Information


if __name__ == '__main__':
    sha3int = int(Web3.sha3(text='withdraw()').hex(),16)
    print(sha3int)
    from z3 import BitVecVal,BitVec
    sha3bv = BitVecVal(sha3int,256)
    print(sha3bv.as_long())
