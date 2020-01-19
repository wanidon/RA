from data_structures import Stack, Memory, MsgData, Storage, Returndata, ExecutionEnvironment, WorldState, MachineState, BasicBlock, Account
from control_flow_manager import ControlFlowManager
from web3 import Web3
from z3 import BV2Int, Int2BV, And, Or, Xor, Not, If, BitVecRef, BitVecNumRef, Concat, Extract, simplify, Solver, sat, unsat, UDiv, URem, Concat
from utils import BitVec256, BitVecVal256, pdbg, sign, BitVecOne256, BitVecZero256, bv_to_signed_int
from collections import defaultdict
from fee_schedule import c
from copy import deepcopy
from exceptions import DevelopmentErorr
from sha3 import keccak_256 # this needs pysha3


WORDBITSIZE = 256
WORDBYTESIZE = WORDBITSIZE // 8

class VM():
    def __init__(self, world_state: WorldState):

        self.σ = world_state
        self.primary_contracts = []
        self.primary_contract_index = 0
        self.secondary_contract = None
        self.tertiary_contracts = []
        # self.exec_env_num = 0

    def add_primary_contract(self, bytecode:str):
        addr = self.σ.add_account(bytecode)
        self.primary_contracts.append(addr)
        return addr

    def add_secondary_contract(self, bytecode:str):
        self.secondary_contract = self.σ.add_account(bytecode)

    def add_tertiary_contract(self, bytecodes:list):
        for b in bytecodes:
            self.tertiary_contracts.append(self.σ.add_account(b))

    def init_state(self, addr: BitVecRef, value: BitVecRef = None):


        account = self.σ.accounts[str(addr)]


        # self.exec_env_num += 1

        µ = MachineState()
        I = ExecutionEnvironment(
                                 Ia=addr,
                                 Ib=account.bytecode,
                                 Iv=value)

        block = BasicBlock(block_number=0, machine_state=µ, exec_env=I)
        self.cfmanager.set_procesisng_block(block)




        # # 主たるコントラクトである場合
        # if exec_env is None:
        #
        #     # TODO: アカウントごとの番号ではなく実行ごとの番号
        #     exec_env_num = account.get_account_num()
        #
        #     self.I = Execution_environment(
        #         exec_env_num, # as exec_env_num
        #         addr,
        #         BitVec256('Io_{}'.format(exec_env_num)),
        #         BitVec256('Ip_{}'.format(exec_env_num)),
        #         [], # empty data
        #         BitVec256('Is_{}'.format(exec_env_num)),
        #         BitVec256('Iv_{}'.format(exec_env_num)),
        #         account.bytecode,
        #         {}, # TODO: blockheader IH
        #         0,
        #         True)
        #
        #
        #         # BitVecRef, Io: BitVecRef, Ip: BitVecRef, Id: BitVecRef, Is: BitVecRef, Iv: BitVecRef, Ib: BitVecRef, IH: dict, Ie: int, Iw: bool):
        #     block = BasicBlock(account.get_account_num(),
        #                             0,
        #                             self.µ)
        #     self.CfgManager = CfgManager(exec_env_num)
        #     self.CfgManager.set_procesisng_block(block)
        #
        #
        #
        # # 従たるコントラクトである場合
        # else:
        #     self.I = exec_env
        #     self.µ.stack = stack
        #     self.µ.memory = memory
        #     if storage is not None:
        #         self.µ.storage = storage
        #     if sender is not None:
        #         self.I.msg_sender = sender
        #
        #     self.CfgManager.set_procesisng_block(block)

    def run_all(self):
        import sys
        while self.primary_contract_index < len(self.primary_contracts):
            sys.stderr.write('run a contract¥n')
            self.cfmanager = ControlFlowManager()
            a = self.primary_contracts[self.primary_contract_index]
            self.init_state(a)
            self.get_exec_env().get_msg_data().set_function_id()
            self.run()
            print(self.cfmanager.show_all())
            name, cfg = self.cfmanager.gen_CFG()


            print(name)
            with open(name + '.dot', 'w') as f:
                f.write(cfg)
            self.primary_contract_index += 1
            self.show_vm_state()

    def show_vm_state(self):
        # I
        print('----I--------')
        self.get_exec_env().show_all()
        # µ
        print('----µ--------')
        self.get_machine_state().show_all()
        # CFG
        print('----cfmanager------')
        self.cfmanager.show_all()

    # getter
    def get_processing_block(self) -> BasicBlock:
        return self.cfmanager.processing_block

    def get_exec_env(self) -> ExecutionEnvironment:
        return self.get_processing_block().get_exec_env()

    def get_machine_state(self) -> MachineState:
        return self.get_processing_block().get_machine_state()

    def get_address(self) -> BitVecRef:
        return self.get_exec_env().this_address

    def get_account_num(self) -> int:
        return self.σ.get_account(self.get_address()).get_account_num()

    def get_account_balance(self, addr=None) -> BitVecRef:
        addr = str(self.get_address()) if addr is None else addr

        return self.σ.get_account(addr).get_balance()

    def get_origin(self) -> BitVecRef:
        return self.get_exec_env().tx_originator

    def get_caller(self) -> BitVecRef:
        return self.get_exec_env().msg_sender

    def get_value(self) -> BitVecRef:
        return self.get_exec_env().msg_value

    def get_data(self) -> MsgData:
        return self.get_exec_env().msg_data

    def get_code(self) -> str:
        return self.get_exec_env().this_code

    def get_gasprice(self) -> BitVecRef:
        return self.get_exec_env().gasprice


    # for manipulating components
    def get_pc(self):
        return self.get_machine_state().pc

    def set_pc(self, pc):
        self.cfmanager.processing_block.machine_state.pc = pc

    def push_to_stack(self, value):
        self.get_machine_state().get_stack().push(value)

    def pop_from_stack(self):
        return self.get_machine_state().stack.pop()

    def dup_on_stack(self, x):
        self.cfmanager.processing_block.machine_state.stack.op_dupx(x)

    def jumped(self):
        return self.cfmanager.processing_block.jumpflag

    def reach_jumpdest(self):
        self.cfmanager.processing_block.jumpflag = False
    # def swapx_on_stack(self,x):
    #     self.CfgManager.processing_block.machine_state.get_stack().swapx(x)
    #
    # def dupx_on_stack(self, x):
    #     self.CfgManager.processing_block.machine_state.get_stack().dupx(x)












    # for utility
    def increment_pc(self):
        self.get_machine_state().set_pc(self.get_machine_state().get_pc() + 1)

    def get_byte_from_bytecode(self):
        return self.get_exec_env().this_code[self.get_pc()*2:self.get_pc()*2+2]


    # 現状ではrun中にjumpdestかを確認
    def check_jumpdest(self, dest:BitVecNumRef):
        d = dest.as_long()
        return True if self.get_exec_env().this_code[d*2:d*2+2] == '5b' else False

    def convert_to_expression(self, condition):
        if isinstance(condition, BitVecNumRef):
            if condition.as_long() == 0:
                return False
            else:
                return True
        else:
            return condition

    def branch(self, continuable, jumpable, condition):
        self.cfmanager.inherit_from_processing_block(continuable, jumpable, condition)

    def external_call(self,
                      # addr:BitVecRef,
                      # account_number:int,
                      exec_env:ExecutionEnvironment,
                      #machine_state:MachineState=None
                      ):
        self.cfmanager.external_call(# addr,
                                     # account_number,
                                     exec_env)

    def set_jumpdest(self, dest):
        self.cfmanager.processing_block.set_jumpdest(dest)

    def get_jumpdest(self):
        return self.cfmanager.processing_block.get_jumpdest()

    def add_immediatevalue(self, iv):
        self.cfmanager.add_immediatevalue(iv)

    def run(self):
        while True:

            if self.cfmanager.visited_address[self.get_exec_env().get_exec_env_id()][self.get_pc()]:
                import sys
                sys.stderr.write(str())
                sys.stderr.write('--{}:visited--'.format(self.get_pc()))
                # # TODO: 終了系の命令でrollbackを実行
                # if self.cfmanager.is_dfs_stack_empty():
                #     return
                # else:
                #     self.cfmanager.rollback_from_dfs_stack()
                #     continue
            else:
                self.cfmanager.visited_address[self.get_exec_env().get_exec_env_id()][self.get_pc()] = True





            if self.get_machine_state().get_pc() >= len(
                    self.get_exec_env().this_code) // 2:
                raise DevelopmentErorr

            hex_opcode = self.get_byte_from_bytecode()
            mnemonic = self.hex_to_mnemonic(hex_opcode)
            print('pc=', self.get_pc(), type(self.get_pc()), mnemonic)


            if self.jumped():
                if mnemonic != 'JUMPDEST':
                    # TODO: exception
                    print('jumped but not jumpdest')
                else:
                    self.reach_jumpdest()

            elif mnemonic == 'JUMPDEST':
                self.cfmanager.search_existing_block(
                        self.get_exec_env().get_exec_env_id(),
                        self.get_pc()
                )
                self.cfmanager.visited_address[self.get_exec_env().get_exec_env_id()][self.get_pc()] = True
                import sys
                sys.stderr.write(str(self.get_pc()))

                pass




            self.cfmanager.add_mnemonic(mnemonic)
            func, num_inputs, num_output, *funcarg = self.mnemonic_to_func(mnemonic)
            s = []
            self.cfmanager.processing_block.get_machine_state().set_gas( simplify(
                self.cfmanager.processing_block.get_gas() -
                c(
                    self.σ,
                    self.cfmanager.processing_block.get_machine_state(),
                    self.cfmanager.processing_block.get_exec_env()
                )))
            # self.µ.gas = self.µ.gas - BitVecVal256(c(self.σ, self.µ, self.I))
            for i in range(num_inputs):
                s.append(deepcopy(self.pop_from_stack()))
            ret = func(s, *funcarg)
            if ret is False:
                break

    def hex_to_mnemonic(self, hex: str):
        d = defaultdict(lambda: 'INVALID')
        d['00'] = 'STOP'
        d['01'] = 'ADD'
        d['02'] = 'MUL'
        d['03'] = 'SUB'
        d['04'] = 'DIV'
        d['05'] = 'SDIV'
        d['06'] = 'MOD'
        d['07'] = 'SMOD'
        d['08'] = 'ADDMOD'
        d['09'] = 'MULMOD'
        d['0a'] = 'EXP'
        d['0b'] = 'SIGNEXTEND'

        d['10'] = 'LT'
        d['11'] = 'GT'
        d['12'] = 'SLT'
        d['13'] = 'SGT'
        d['14'] = 'EQ'
        d['15'] = 'ISZERO'
        d['16'] = 'AND'
        d['17'] = 'OR'
        d['18'] = 'XOR'
        d['19'] = 'NOT'
        d['1a'] = 'BYTE'
        d['20'] = 'SHA3'

        d['30'] = 'ADDRESS'
        d['31'] = 'BALANCE'
        d['32'] = 'ORIGIN'
        d['33'] = 'CALLER'
        d['34'] = 'CALLVALUE'
        d['35'] = 'CALLDATALOAD'
        d['36'] = 'CALLDATASIZE'
        d['37'] = 'CODEDATACOPY'
        d['38'] = 'CODESIZE'
        d['39'] = 'CODECOPY'
        d['3a'] = 'GASPRICE'
        d['3b'] = 'EXTCODESIZE'
        d['3c'] = 'EXTCODECOPY'
        d['3d'] = 'RETURNDATASIZE'
        d['3e'] = 'RETURNDATACOPY'

        d['40'] = 'BLOCKHASH'
        d['41'] = 'COINBASE'
        d['42'] = 'TIMESTAMP'
        d['43'] = 'NUMBER'
        d['44'] = 'DIFFICULTY'
        d['45'] = 'GASLIMIT'

        d['50'] = 'POP'
        d['51'] = 'MLOAD'
        d['52'] = 'MSTORE'
        d['53'] = 'MSTORE8'
        d['54'] = 'SLOAD'
        d['55'] = 'SSTORE'
        d['56'] = 'JUMP'
        d['57'] = 'JUMPI'
        d['58'] = 'PC'
        d['59'] = 'MSIZE'
        d['5a'] = 'GAS'
        d['5b'] = 'JUMPDEST'

        d['60'] = 'PUSH1'
        d['61'] = 'PUSH2'
        d['62'] = 'PUSH3'
        d['63'] = 'PUSH4'
        d['64'] = 'PUSH5'
        d['65'] = 'PUSH6'
        d['66'] = 'PUSH7'
        d['67'] = 'PUSH8'
        d['68'] = 'PUSH9'
        d['69'] = 'PUSH10'
        d['6a'] = 'PUSH11'
        d['6b'] = 'PUSH12'
        d['6c'] = 'PUSH13'
        d['6d'] = 'PUSH14'
        d['6e'] = 'PUSH15'
        d['6f'] = 'PUSH16'
        d['70'] = 'PUSH17'
        d['71'] = 'PUSH18'
        d['72'] = 'PUSH19'
        d['73'] = 'PUSH20'
        d['74'] = 'PUSH21'
        d['75'] = 'PUSH22'
        d['76'] = 'PUSH23'
        d['77'] = 'PUSH24'
        d['78'] = 'PUSH25'
        d['79'] = 'PUSH26'
        d['7a'] = 'PUSH27'
        d['7b'] = 'PUSH28'
        d['7c'] = 'PUSH29'
        d['7d'] = 'PUSH30'
        d['7e'] = 'PUSH31'
        d['7f'] = 'PUSH32'

        d['80'] = 'DUP1'
        d['81'] = 'DUP2'
        d['82'] = 'DUP3'
        d['83'] = 'DUP4'
        d['84'] = 'DUP5'
        d['85'] = 'DUP6'
        d['86'] = 'DUP7'
        d['87'] = 'DUP8'
        d['88'] = 'DUP9'
        d['89'] = 'DUP10'
        d['8a'] = 'DUP11'
        d['8b'] = 'DUP12'
        d['8c'] = 'DUP13'
        d['8d'] = 'DUP14'
        d['8e'] = 'DUP15'
        d['8f'] = 'DUP16'

        d['90'] = 'SWAP1'
        d['91'] = 'SWAP2'
        d['92'] = 'SWAP3'
        d['93'] = 'SWAP4'
        d['94'] = 'SWAP5'
        d['95'] = 'SWAP6'
        d['96'] = 'SWAP7'
        d['97'] = 'SWAP8'
        d['98'] = 'SWAP9'
        d['99'] = 'SWAP10'
        d['9a'] = 'SWAP11'
        d['9b'] = 'SWAP12'
        d['9c'] = 'SWAP13'
        d['9d'] = 'SWAP14'
        d['9e'] = 'SWAP15'
        d['9f'] = 'SWAP16'







        d['f0'] = 'CREATE'
        d['f1'] = 'CALL'
        d['f2'] = 'CALLCODE'
        d['f3'] = 'RETURN'
        d['f4'] = 'DELEGATECALL'
        d['fa'] = 'STATICCALL'
        d['fd'] = 'REVERT'






        d['fe'] = 'INVALID'

        return d[hex]

    def mnemonic_to_func(self, mnemonic: str):

        d = {
            # 0s
            'STOP': (self.op_stop, 0, 0),
            'ADD': (self.op_add, 2, 1),
            'MUL': (self.op_mul, 2, 1),
            'SUB': (self.op_sub, 2, 1),
            'DIV': (self.op_div, 2, 1),
            'SDIV': (self.op_sdiv, 2, 1),
            'MOD': (self.op_mod, 2, 1),
            'SMOD': (self.op_smod, 2, 1),
            'ADDMOD': (self.op_addmod, 3, 1),
            'MULMOD': (self.op_mulmod, 3, 1),
            'EXP': (self.op_exp, 2, 1),
            'SIGNEXTEND': (self.op_signextend, 2, 1),

            # 10s
            'LT': (self.op_lt, 2, 1),
            'GT': (self.op_gt, 2, 1),
            'SLT': (self.op_slt, 2, 1),
            'SGT': (self.op_sgt, 2, 1),
            'EQ': (self.op_eq, 2, 1),
            'ISZERO': (self.op_iszero, 1, 1),
            'AND': (self.op_and, 2, 1),
            'OR': (self.op_or, 2, 1),
            'XOR': (self.op_xor, 2, 1),
            'NOT': (self.op_not, 2, 1),
            'BYTE': (self.op_byte, 2, 1),

        # #     d['10'] = 'LT'
        # d['11'] = 'GT'
        # d['12'] = 'SLT'
        # d['13'] = 'SGT'
        # d['14'] = 'EQ'
        # d['15'] = 'ISZERO'
        # d['16'] = 'AND'
        # d['17'] = 'OR'
        # d['18'] = 'XOR'
        # d['19'] = 'NOT'
        # d['1a'] = 'BYTE'

            # 20s
            'SHA3': (self.op_sha3, 2, 1),

            # 30s
            'ADDRESS': (self.op_address, 0, 1),
            'BALANCE': (self.op_balance, 1, 1),
            'ORIGIN' : (self.op_origin, 0, 1),
            'CALLER' : (self.op_caller, 0, 1),
            'CALLVALUE' : (self.op_callvalue, 0, 1),
            'CALLDATALOAD' : (self.op_calldataload, 1, 1),
            'CALLDATASIZE' : (self.op_calldatasize, 0, 1),
            'CALLDATACOPY' : (self.op_calldatacopy, 3, 0),
            'CODESIZE' : (self.op_codesize, 0, 1),
            'CODECOPY' : (self.op_codecopy, 3, 0),
            'GASPRICE' : (self.op_gasprice, 0, 1),
            'EXTCODESIZE': (self.op_extcodesize, 1, 1),
            'EXTCODECOPY': (self.op_extcodecopy, 3 ,0),
            'RETURNDATASIZE': (self.op_returndatasize, 0, 1),
            'RETURNDATACOPY': (self.op_returndatacopy, 3, 0),

            # 40s
            'BLOCKHASH': (self.op_blockhash, 1, 1),
            'COINBASE': (self.op_coinbase, 0, 1),
            'TIMESTAMP': (self.op_timestamp, 0, 1),
            'NUMBER': (self.op_number, 0, 1),
            'DIFFICULTY': (self.op_difficulty, 0, 1),
            'GASLIMIT': (self.op_gaslimit, 0, 1),

            # 50s
            'POP': (self.op_pop, 1, 0),
            'MLOAD': (self.op_mload, 1, 1),
            'MSTORE': (self.op_mstore, 2, 0),
            'MSTORE8': (self.op_mstore8, 2, 0),
            'SLOAD': (self.op_sload, 1, 1),
            'SSTORE': (self.op_sstore, 2, 0),
            'JUMP': (self.op_jump, 1, 0),
            'JUMPI': (self.op_jumpi, 2, 0),
            'PC': (self.op_pc, 0, 1),
            'MSIZE': (self.op_msize, 0, 1),
            'GAS': (self.op_gas, 0, 1),
            'JUMPDEST': (self.op_jumpdest, 0, 0),


            # 60s & 70s: Push Operations
            'PUSH1': (self.op_pushx, 0, 1, 1),
            'PUSH2': (self.op_pushx, 0, 1, 2),
            'PUSH3': (self.op_pushx, 0, 1, 3),
            'PUSH4': (self.op_pushx, 0, 1, 4),
            'PUSH5': (self.op_pushx, 0, 1, 5),
            'PUSH6': (self.op_pushx, 0, 1, 6),
            'PUSH7': (self.op_pushx, 0, 1, 7),
            'PUSH8': (self.op_pushx, 0, 1, 8),
            'PUSH9': (self.op_pushx, 0, 1, 9),
            'PUSH10': (self.op_pushx, 0, 1, 10),
            'PUSH11': (self.op_pushx, 0, 1, 11),
            'PUSH12': (self.op_pushx, 0, 1, 12),
            'PUSH13': (self.op_pushx, 0, 1, 13),
            'PUSH14': (self.op_pushx, 0, 1, 14),
            'PUSH15': (self.op_pushx, 0, 1, 15),
            'PUSH16': (self.op_pushx, 0, 1, 16),
            'PUSH17': (self.op_pushx, 0, 1, 17),
            'PUSH18': (self.op_pushx, 0, 1, 18),
            'PUSH19': (self.op_pushx, 0, 1, 19),
            'PUSH20': (self.op_pushx, 0, 1, 20),
            'PUSH21': (self.op_pushx, 0, 1, 21),
            'PUSH22': (self.op_pushx, 0, 1, 22),
            'PUSH23': (self.op_pushx, 0, 1, 23),
            'PUSH24': (self.op_pushx, 0, 1, 24),
            'PUSH25': (self.op_pushx, 0, 1, 25),
            'PUSH26': (self.op_pushx, 0, 1, 26),
            'PUSH27': (self.op_pushx, 0, 1, 27),
            'PUSH28': (self.op_pushx, 0, 1, 28),
            'PUSH29': (self.op_pushx, 0, 1, 29),
            'PUSH30': (self.op_pushx, 0, 1, 30),
            'PUSH31': (self.op_pushx, 0, 1, 31),
            'PUSH32': (self.op_pushx, 0, 1, 32),

            # 80s: Duplication Operations
            'DUP1': (self.op_dupx, 1, 2),
            'DUP2': (self.op_dupx, 2, 3),
            'DUP3': (self.op_dupx, 3, 4),
            'DUP4': (self.op_dupx, 4, 5),
            'DUP5': (self.op_dupx, 5, 6),
            'DUP6': (self.op_dupx, 6, 7),
            'DUP7': (self.op_dupx, 7, 8),
            'DUP8': (self.op_dupx, 8, 9),
            'DUP9': (self.op_dupx, 9, 10),
            'DUP10': (self.op_dupx, 10, 11),
            'DUP11': (self.op_dupx, 11, 12),
            'DUP12': (self.op_dupx, 12, 13),
            'DUP13': (self.op_dupx, 13, 14),
            'DUP14': (self.op_dupx, 14, 15),
            'DUP15': (self.op_dupx, 15, 16),
            'DUP16': (self.op_dupx, 16, 17),

            # 90s: Exchange Operations
            'SWAP1': (self.op_swapx, 2, 2),
            'SWAP2': (self.op_swapx, 3, 3),
            'SWAP3': (self.op_swapx, 4, 4),
            'SWAP4': (self.op_swapx, 5, 5),
            'SWAP5': (self.op_swapx, 6, 6),
            'SWAP6': (self.op_swapx, 7, 7),
            'SWAP7': (self.op_swapx, 8, 8),
            'SWAP8': (self.op_swapx, 9, 9),
            'SWAP9': (self.op_swapx, 10, 10),
            'SWAP10': (self.op_swapx, 11, 11),
            'SWAP11': (self.op_swapx, 12, 12),
            'SWAP12': (self.op_swapx, 13, 13),
            'SWAP13': (self.op_swapx, 14, 14),
            'SWAP14': (self.op_swapx, 15, 15),
            'SWAP15': (self.op_swapx, 16, 16),
            'SWAP16': (self.op_swapx, 17, 17),

            # a0s: Logging Operations
            # f0s: System operations
            'CREATE': (self.op_create, 3, 1),
            'CALL': (self.op_call, 7, 1),
            'CALLCODE': (self.op_callcode, 7, 1),
            'RETURN': (self.op_return, 2, 0),
            'DELEGATECALL': (self.op_delegatecall, 6, 1),





            'REVERT': (self.op_revert, 2, 0),






            'INVALID': (self.op_stop, 0, 0)  # TODO implement exceptional halting

        }
        return d[mnemonic]

        # 0s: Stop and Arithmetic Operations

    def op_stop(self, s):
        print('path condition=', self.cfmanager.processing_block.get_path_condition())
        if self.cfmanager.is_dfs_stack_empty():
            return False
        else:
            current_block = self.get_processing_block()
            current_pc = self.get_pc()
            next_block = self.cfmanager.rollback_from_dfs_stack()
            next_pc = self.get_pc()
            # if next_pc < current_pc and self.cfmanager.visited_address[self.get_exec_env().get_exec_env_id()][next_pc]:
            #     return False
            if self.cfmanager.visited_address[self.get_exec_env().get_exec_env_id()][next_pc]:
                print('execution stop!')
                return False
            else:
                self.cfmanager.set_procesisng_block(next_block)





    def op_add(self, s):
        self.push_to_stack(simplify(s[0] + s[1]))
        self.increment_pc()

    def op_mul(self, s):
        self.push_to_stack(simplify(s[0] * s[1]))
        self.increment_pc()

    def op_sub(self, s):
        self.push_to_stack(simplify(s[0] - s[1]))
        self.increment_pc()

    def op_div(self, s):
        if type(s[1]) == BitVecNumRef and s[1].as_long() == 0:
            self.push_to_stack(BitVecVal256(0))
        else:
            self.push_to_stack(simplify(s[0] / s[1]))
        self.increment_pc()

    def op_sdiv(self, s):
        if isinstance(s[1], BitVecNumRef) and s[1].as_singed_long() == 0:
            self.push_to_stack(BitVecVal256(0))
        elif isinstance(s[0], BitVecNumRef) and isinstance(s[1], BitVecNumRef):
            if s[0].as_signed_long() == -2**255 and s[1].as_signed_long() == -1:
                self.push_to_stack(BitVecVal256(-2**255))
            else:
                self.push_to_stack(BitVecVal256(s[0].as_signed_long() // s[1].as_singed_long()))
        else:
            # sgn(μs[0] ÷ μs[1])⌊|μs[0] ÷ μs[1]|⌋ otherwise
            # TODO: when s[0] or s[1] is symbol variable
            # TODO: use z3 singed div
            self.push_to_stack(simplify(s[0]/s[1]))

        self.increment_pc()

    def op_mod(self, s):
        if isinstance(s[1], BitVecNumRef) and s[1].as_long() == 0:
            self.push_to_stack(BitVecVal256(0))
        else:
            self.push_to_stack(simplify(URem(s[0], s[1])))
        self.increment_pc()

    def op_smod(self, s):
        if isinstance(s[1], BitVecNumRef) and s[1].as_signed_long() == 0:
            self.push_to_stack(BitVecVal256(0))
        else:
            self.push_to_stack(simplify(s[0] % s[1]))
        self.increment_pc()

    def op_addmod(self, s):
        if isinstance(s[2], BitVecNumRef) and s[2].as_long() == 0:
            self.push_to_stack(BitVecVal256(0))
        else:
            s0 = s[0].as_long() if isinstance(s[0], BitVecNumRef) else s[0]
            s1 = s[1].as_long() if isinstance(s[1], BitVecNumRef) else s[1]
            self.push_to_stack(simplify(URem((s0 + s1), s[2])))
        self.increment_pc()

    def op_mulmod(self, s):
        if isinstance(s[2], BitVecNumRef) and s[2].as_long() == 0:
            self.push_to_stack(BitVecVal256(0))
        # TODO check modulo
        else:
            s0 = s[0].as_long() if isinstance(s[0], BitVecNumRef) else s[0]
            s1 = s[1].as_long() if isinstance(s[1], BitVecNumRef) else s[1]
            self.push_to_stack(URem((s0 * s1), s[2]))
        self.increment_pc()

    def op_exp(self, s):
        s0 = s[0].as_long() if isinstance(s[0], BitVecNumRef) else s[0]
        if isinstance(s[1], BitVecNumRef):
            if isinstance(s[0], BitVecNumRef):
                s1 = s[1].as_long()
                self.push_to_stack(BitVecVal256(s0 ** s1))
            else:
                s1 = int(s[1].as_long())
                v = s0
                for i in range(s1 - 1):
                    v *= v
                self.push_to_stack(simplify(v))

        else:
            # TODO for bitvec
            pass

        self.increment_pc()

    # TODO
    def op_signextend(self, s):
        # TODO: if s[0] is symbol variable
        # TODO: test
        if isinstance(s[0], BitVecVal256):
            t = 256 - 8*(s[0].as_long() + 1)
            sign = Extract(t, t, s[1])
            ret = s[0]
            for i in range(t+1):
                ret = simplify(Concat(sign, ret))
            self.push_to_stack(ret)
        self.increment_pc()

        # 10s: Comparison & Bitwise Logic Operations

    def op_lt(self, s):
        self.push_to_stack(If(BV2Int(s[0]) < BV2Int(s[1]), BitVecOne256(), BitVecZero256()))
        self.increment_pc()

    def op_gt(self, s):
        self.push_to_stack(If(BV2Int(s[0]) > BV2Int(s[1]), BitVecOne256(), BitVecZero256()))
        self.increment_pc()

    def op_slt(self, s):
        self.push_to_stack(If(bv_to_signed_int(s[0]) < bv_to_signed_int(s[1]), BitVecOne256(), BitVecZero256()))
        self.increment_pc()

    def op_sgt(self, s):
        self.push_to_stack(If(bv_to_signed_int(s[0]) > bv_to_signed_int(s[1]), BitVecOne256(), BitVecZero256()))
        self.increment_pc()

    def op_eq(self, s):
        self.push_to_stack(If(BV2Int(s[0]) == BV2Int(s[1]), BitVecOne256(), BitVecZero256()))
        self.increment_pc()

    def op_iszero(self, s):
        self.push_to_stack(If(BV2Int(s[0]) == 0, BitVecOne256(), BitVecZero256()))
        self.increment_pc()

    def op_and(self, s):
        self.push_to_stack(simplify(s[0] & s[1]))
        self.increment_pc()

    def op_or(self, s):
        self.push_to_stack(simplify(s[0] | s[1]))
        self.increment_pc()

    def op_xor(self, s):
        self.push_to_stack(simplify(s[0] ^ s[1]))
        self.increment_pc()

    def op_not(self, s):
        self.push_to_stack(~s[0])
        self.increment_pc()

    def op_byte(self, s):
        mask = Int2BV((2 ** 8 - 1) * 2 ** (BV2Int(s[0]) * 8), 256)
        # extract a byte
        a = mask & s[1]
        # s[0] bit shift
        b = Int2BV(2 ** (BV2Int(s[0]) * 8), 256)
        self.push_to_stack(simplify(UDiv(a, b)))
        self.increment_pc()


        # 20s: SHA3
    def op_sha3(self, s):

        # from web3 import Web3
        # hex(Web3.toInt(Web3.soliditySha3(['uint8'], [1])))
        # TODO
        if isinstance(s[0],BitVecNumRef) and isinstance(s[1],BitVecNumRef):
            offset = s[0].as_long()
            length = s[1].as_long()
            data = None
            for i in range(offset, offset+length):
                d = self.get_machine_state().get_memory().get_one_byte(i)
                if not isinstance(d, BitVecNumRef):
                    data = BitVec256('SHA3-VALUE')
                    break
                data += bytes(self.get_machine_state().get_memory().get_one_byte(i))

        self.push_to_stack(data)
        self.increment_pc()
        #
        # pass
        # offset = self.stack.pop()
        # length = self.stack.pop()

        # 30s: Environmental Information
    def op_address(self, s):
        self.push_to_stack(self.get_address())
        self.increment_pc()

    def op_balance(self, s):
        self.push_to_stack(self.get_account_balance())
        self.increment_pc()

    def op_origin(self, s):
        self.push_to_stack(self.get_origin())
        self.increment_pc()

    def op_caller(self, s):
        self.push_to_stack(self.get_caller())
        self.increment_pc()

    def op_callvalue(self, s):
        self.push_to_stack(self.get_value())
        self.increment_pc()

    def op_calldataload(self, s):
        msg_data = self.get_data().duplicate()
        if not isinstance(s[0],BitVecNumRef):
            raise DevelopmentErorr()
        memsize = msg_data.size()

        for i in range(memsize, s[0].as_long()+WORDBYTESIZE):
            msg_data.mstore8(i, BitVecZero256())

        self.push_to_stack(msg_data.mload(s[0]))
        self.increment_pc()

    def op_calldatasize(self, s):
        self.push_to_stack(BitVecVal256(self.get_data().size()))
        self.increment_pc()

    def op_calldatacopy(self,s):
        if not (isinstance(s[0], BitVecNumRef) and isinstance(s[1], BitVecNumRef) and isinstance(s[2], BitVecNumRef)):
            raise DevelopmentErorr()

        memoffset = s[0].as_long()
        dataoffset = s[1].as_long()
        copysize = s[2].as_long()

        data = self.get_data()
        tmpdata = []

        for i in range(dataoffset, dataoffset+copysize):
            tmpdata.append(data.get_one_byte(i))

        memory = self.get_machine_state().get_memory()
        for i in range(memoffset, copysize):
            memory.mstore8(i, tmpdata[i])

        self.increment_pc()

    def op_codesize(self, s):
        self.push_to_stack(BitVecVal256(len(self.get_code())))
        self.increment_pc()

    def op_codecopy(self, s):
        memoffset = s[0].as_long()
        codeoffset = s[1].as_long() * 2
        copysize = s[2].as_long() * 2

        codesize = len(self.get_code())
        tmpcode = self.get_code()[codeoffset:codeoffset+copysize] + '00' * (codeoffset + copysize - codesize)

        memory = self.get_machine_state().get_memory()
        print('memoffset=',memoffset,'codeoffset=',codeoffset,'copysize=',copysize,'codesize=',codesize)
        print('tmpcode=',tmpcode[:20],'copysize=',copysize)
        for i in range(copysize//2):
            # print(tmpcode[i*2:i*2+2],type(tmpcode[i*2:i*2+2]))
            # print(i,int(tmpcode[i*2:i*2+2],16))
            memory.mstore8(memoffset+i, BitVecVal256(int(tmpcode[i*2:i*2+2],16)))

        self.increment_pc()

    def op_gasprice(self, s):
        self.push_to_stack(self.get_gasprice())
        self.increment_pc()

    def op_extcodesize(self, s):
        addr = str(simplify(s[0] % 2**160))
        self.push_to_stack(BitVecVal256(len(self.σ.get_account(addr).get_bytecode())))

    def op_extcodecopy(self, s):
        addr = s[0] % 2**160
        memoffset = s[1].as_long()
        codeoffset = s[2].as_long()
        copysize = s[3].as_long()
        code = self.σ.get_account(addr).get_bytecode()
        codesize = len(code)
        tmpcode = code[codeoffset:copysize] + '00' * (codeoffset + copysize - codesize)
        memory = self.get_machine_state().get_memory()
        for i in range(memoffset, copysize):
            memory.mstore8(BitVecVal256(i), BitVecVal256(tmpcode[i*2:i*2+2]))
        self.increment_pc()

    def op_returndatasize(self, s):
        # TODO
        pass

    def op_returndatacopy(self, s):
        # TODO
        pass










        # 40s: Block Information
    def op_blockhash(self, s):
        n = BV2Int(s[0])
        current_block_number = BV2Int(self.get_exec_env().get_block_header().get_block_number())
        parent_hash = self.get_exec_env().get_block_header().get_parent_hash()
        a = current_block_number - n
        self.push_to_stack(If(Or(a <= 0, 256 <= a), BitVecZero256(),
                              If(a == 1, parent_hash, BitVec256('block_hash_' + str(n)))))
        self.increment_pc()

    def op_coinbase(self, s):
        self.push_to_stack(self.get_exec_env().get_block_header().get_beneficiary())
        self.increment_pc()

    def op_timestamp(self, s):
        self.push_to_stack(self.get_exec_env().get_block_header().get_timestamp())
        self.increment_pc()

    def op_number(self, s):
        self.push_to_stack(self.get_exec_env().get_block_header().get_block_number())
        self.increment_pc()

    def op_difficulty(self, s):
        self.push_to_stack((self.get_exec_env().get_block_header().get_difficulty()))
        self.increment_pc()

    def op_gaslimit(self, s):
        self.push_to_stack(self.get_exec_env().get_block_header().get_gaslimit())
        self.increment_pc()


        # 50s: Stack, Memory, Storage and Flow Operations
    def op_pop(self, s):
        self.increment_pc()

    def op_mload(self, s):
        self.push_to_stack(self.get_machine_state().get_memory().mload(s[0]))
        self.increment_pc()

    def op_mstore(self, s):
        self.get_machine_state().get_memory().mstore(s[0], s[1])
        self.increment_pc()

    def op_mstore8(self, s):
        self.get_machine_state().get_memory().mstore8(s[0],s[1])
        self.increment_pc()

    def op_sload(self, s):
        self.push_to_stack(self.get_machine_state().get_storage().sload(s[0]))
        self.increment_pc()

    def op_sstore(self, s):
        self.get_machine_state().get_storage().sstore(s[0],s[1])
        self.increment_pc()

    def op_jump(self, s):
        if not isinstance(s[0], BitVecNumRef):
            raise DevelopmentErorr('cannot to jump to address expressed with symbol variable')
        # 現状ではrun中にjumpdestかを確認
        # if not self.check_jumpdest(s[0]):
        #     raise
        jumpdest = s[0]
        self.set_jumpdest(jumpdest)
        self.branch(continuable=False, jumpable=True, condition=True)



    def op_jumpi(self, s):

        jumpdest = s[0]
        condition = self.convert_to_expression(s[1])

        self.set_jumpdest(jumpdest)
        print('row jump condition = ', s[1])
        print('jump condition = ', condition, type(condition), self.get_pc())
        # 式でないただのシンボル変数なら，0でないかを判定
        if type(condition) == BitVecRef:
            condition = condition != 0

        s = Solver()
        s.push()
        # ジャンプ可能か
        s.append(condition)
        jumpable = s.check() == sat


        s.pop()
        # 継続可能か
        s.append(Not(condition))
        continuable = s.check() == sat

        self.branch(continuable, jumpable, condition)

    def op_pc(self, s):
        self.push_to_stack(self.get_machine_state().get_pc())
        self.increment_pc()

    def op_msize(self, s):
        self.push_to_stack(self.get_machine_state().get_memory().size())
        self.increment_pc()

    def op_gas(self, s):
        self.push_to_stack(self.get_machine_state().get_gas())
        self.increment_pc()

    def op_jumpdest(self, s):
        self.increment_pc()


    # 60s & 70s: Push Operations
    def op_pushx(self, s, x):
        # extract value
        v = ''
        for i in range(x):
            self.increment_pc()
            v += self.get_byte_from_bytecode()
        self.add_immediatevalue(v)
        v = BitVecVal256(int(v, 16))
        self.push_to_stack(v)
        self.increment_pc()
        import sys
        print(v)


    # 80s: Duplication Operations
    def op_dupx(self, s):
        self.get_machine_state().show_all()
        v = deepcopy(s[-1])
        print(s)
        for i in range(len(s)-1,-1,-1):
            self.push_to_stack(s[i])
        self.push_to_stack(v)
        self.increment_pc()

    # 90s: Exchange Operations
    def op_swapx(self, s):
        t = deepcopy(s[0])
        b = deepcopy(s[-1])
        self.push_to_stack(t)
        for i in range(len(s)-2,0,-1):
            self.push_to_stack(s[i])
        self.push_to_stack(b)
        self.increment_pc()

    def op_create(self, s):
        if not (isinstance(s[1], BitVecNumRef) and isinstance(s[2], BitVecNumRef)):
            raise DevelopmentErorr('illegal parameter given to CREATE')

        offset = s[1].as_long()
        length = s[2].as_long()
        new_code = ''
        for i in range(length):
            op = self.get_machine_state().get_memory().get_one_byte(offset+i)
            if not isinstance(op, BitVecNumRef):
                raise DevelopmentErorr('illegal parameter given to CREATE')
            new_code += format(op.as_long(), '02x')


        # generate new execution environment
        exec_env = ExecutionEnvironment(
            Ia=BitVecZero256(),
            Ib=new_code,
            Is=self.get_address(),
            Iv=s[0])
        # call initialization code
        self.external_call(#self.get_account_num(),

                           exec_env=exec_env)






    def op_call(self, s):
        print(type(self.secondary_contract))
        if self.secondary_contract is None:
            self.push_to_stack(BitVec256('call_succeeds_{}_{}'.format(self.get_exec_env().get_exec_env_id(), self.get_pc()*2)))
            self.increment_pc()
            return
        gas = s[0]
        print(self.get_address(), self.secondary_contract)
        addr = self.secondary_contract if self.get_address() != self.secondary_contract \
            else self.primary_contracts[self.primary_contract_index]
        value = s[2]
        argsOffset = s[3]
        argsLength = s[4]
        retOffset = s[5]
        retLength = s[6]

        if not (isinstance(argsOffset, BitVecNumRef)
                and isinstance(argsLength, BitVecNumRef)
                and isinstance(retOffset, BitVecNumRef)
                and isinstance(retLength, BitVecNumRef)):
            raise DevelopmentErorr()




        pass
    def op_callcode(self, s):
        pass

    def op_return(self, s):
        print('pc=',self.get_pc())
        if not(isinstance(s[0],BitVecNumRef) and isinstance(s[1],BitVecNumRef)):
            self.get_machine_state().show_all()
            raise DevelopmentErorr

        offset = s[0].as_long()

        length = s[1].as_long()

        return_value = ''
        for i in range(offset, offset+length):
            return_value += format(self.get_machine_state().get_memory().get_one_byte(i).as_long(),'02x')
        print(offset, length,return_value[:20],len(return_value))

        if self.cfmanager.get_processing_block().get_call_stack_size() > 0:
            return_block = self.cfmanager.pop_from_call_stack()
            # self.cfmanager.add_edge(self.get_processing_block(), return_block)
            return_block.get_machine_state().set_memory(deepcopy(self.get_machine_state().get_memory()))
            return_block.get_machine_state().set_stack(deepcopy(self.get_machine_state().get_stack()))
            self.cfmanager.processing_block = return_block







            # when the external call was caused by CREATE
            prevpc = return_block.get_pc() - 1
            # import sys
            #
            # sys.stderr.write(str(s[0].size()))
            # sys.stderr.write(str(self.get_account_balance().size()))

            import sys
            sys.stderr.write(return_block.get_exec_env().get_code()[prevpc*2:prevpc*2+2])
            if return_block.get_exec_env().get_code()[prevpc*2:prevpc*2+2] == 'f0':

                addr = self.add_primary_contract(return_value)
                # sys.stderr.write(str(type(addr)))

                # TODO gas calculation
                condition = And(s[0] <= self.get_account_balance(),
                                self.get_machine_state().get_stack().get_stack_size() < 1024)
                print(condition,simplify(If(condition,
                                   addr
                                      , BitVecZero256())))
                self.push_to_stack(simplify(If(condition,
                                   addr
                                      , BitVecZero256())))
                print('aaaaaaaaaaaa')
                self.get_machine_state().show_all()
                print('bbbbbbbbbbb')

        elif self.cfmanager.get_processing_block().get_dfs_stack_size() > 0:
            self.cfmanager.pop_from_dfs_stack()
        else:
            return False


    def op_delegatecall(self, s):
        pass
    def op_revert(self, s):
        if self.cfmanager.get_processing_block().get_call_stack_size() > 0:
            return_block = self.cfmanager.pop_from_call_stack()
            # self.cfmanager.add_edge(self.get_processing_block(),return_block)
            self.cfmanager.set_procesisng_block(return_block)
        else:
            if self.cfmanager.is_dfs_stack_empty():
                return False
            else:
                self.cfmanager.rollback_from_dfs_stack()

    def invalid(self,s):
        # TODO 異常終了

        self.op_stop(s)
if __name__ == '__main__':
    sha3int = int(Web3.sha3(text='withdraw()').hex(),16)
    print(sha3int)
    from z3 import BitVecVal,BitVec
    sha3bv = BitVecVal(sha3int,256)
    print(sha3bv.as_long())
