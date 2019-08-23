from data_structures import Stack, Memory, Storage, Returndata, Execution_environment, WorldState, Machine_state, CFGmanager, BasicBlock
from web3 import Web3


class VM():
    def __init__(self,
                 system_state: WorldState,
                 exe_env: Execution_environment
                 ):

        self.__σ = system_state
        self.I = Execution_environment
        self.__µ = Machine_state()
        self.CFG_manager = CFGmanager()

        self.__tmp_block = BasicBlock()
        self.__call_stack = [] # list of (I,next_pc)
        self.__dfs_stack = [] # list of Basic_block
        #self.returndata = returndata


    # 0s: Stop and Arithmetic Operations
    def stop(self):
        if self.__dfs_stack :



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
