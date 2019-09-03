from data_structures import Stack, Memory, Storage, Returndata, Execution_environment, WorldState, Machine_state, CfgManager, BasicBlock, Account
from web3 import Web3
from z3 import And, Not, BitVecRef, BitVecNumRef, Concat, Extract, simplify
from utils import BitVec256, pdbg



class VM():
    def __init__(self, world_state: WorldState):

        self.σ = world_state

    def init_state(self,
                   addr: BitVecRef,
                   exec_env:Execution_environment=None,
                   stack:Stack=None,
                   memory:Memory=None,
                   storage:Storage=None,
                   sender:BitVecRef=None
                   ):

        self.µ = Machine_state()
        account = self.σ.accounts[addr]

        # 主たるコントラクトである場合
        if exec_env is None:

            exec_env_num = account.get_account_num()

            self.I = Execution_environment(
                exec_env_num, # as exec_env_num
                addr,
                BitVec256('Io_{}'.format(exec_env_num)),
                BitVec256('Ip_{}'.format(exec_env_num)),
                [], # empty data
                BitVec256('Is_{}'.format(exec_env_num)),
                BitVec256('Iv_{}'.format(exec_env_num)),
                account.bytecode,
                {}, # TODO: blockheader IH
                0,
                True)


                # BitVecRef, Io: BitVecRef, Ip: BitVecRef, Id: BitVecRef, Is: BitVecRef, Iv: BitVecRef, Ib: BitVecRef, IH: dict, Ie: int, Iw: bool):
            self.CfgManager = CfgManager(exec_env_num)
            self.__call_stack = []
            self.__dfs_stack = []



        # 従たるコントラクトである場合
        else:
            self.I = exec_env
            self.µ.stack = stack
            self.µ.memory = memory
            if storage is not None:
                self.µ.storage = storage
            if sender is not None:
                self.I.msg_sender = sender



    # 0s: Stop and Arithmetic Operations

    def stop(self):
        if self.__dfs_stack :
            pass



    # 10s: Comparison & Bitwise Logic Operations
    # 20s: SHA3
    def sha3(self):
        offset = self.stack.pop()
        length = self.stack.pop()


    # 30s: Environmental Information


if __name__ == '__main__':
    sha3int = int(Web3.sha3(text='withdraw()').hex(),16)
    print(sha3int)
    from z3 import BitVecVal,BitVec
    sha3bv = BitVecVal(sha3int,256)
    print(sha3bv.as_long())
