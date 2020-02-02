#! /usr/bin/env/ python3
# coding:utf-8

from collections import deque
from copy import deepcopy,copy
from z3 import And, Or, Not, BitVecRef, BitVecNumRef, BoolRef, BitVec, BitVecVal, Concat, Extract, simplify, Int, Solver, unsat, sat, ZeroExt, ExprRef
from utils import BitVec256, BitVecVal256, zero8bit, checkBitVecRef256, dbgredmsg
from exceptions import DevelopmentErorr, SettingError
from constant import RUNNING, TERMINATED, RETURNED, CALLABLE
from collections import defaultdict
from random import random

WORDBITSIZE = 256
WORDBYTESIZE = WORDBITSIZE // 8


class Stack:

    def __init__(self, block_number=0, stdata=None, num_stack_var=0):
        # blockNumber will be VM object's member
        self.__blockNumber = block_number
        self.__stackdata = deque() if stdata is None else stdata
        self.__numStackVar = num_stack_var

    def duplicate(self, new_block_number:int):
        return Stack(new_block_number, deepcopy(self.__stackdata), self.__numStackVar)

    def generateStackVar(self) -> BitVecRef:
        self.__numStackVar += 1
        return BitVec256('stackVar{}-{}'.format(self.__blockNumber, self.__numStackVar))

    def push(self, w:BitVecRef):
        if len(self.__stackdata) < 1024:
            self.__stackdata.append(checkBitVecRef256(w))
            # self.__stackdata.append(w)
        else:
            # TODO stack limit reached 1024
            pass

    def pop(self) -> BitVecRef:
        if len(self.__stackdata) >= 1:
            return checkBitVecRef256(self.__stackdata.pop())
        else:
            # generate a symbolic variable
            # TODO this may cause stack underflow
            return self.generateStackVar()

    def get_stack_size(self) -> int:
        return len(self.__stackdata)

    # def swapx(self, x:int):
    #     if x < 1 or 16 < x:
    #         raise DevelopmentErorr()
    #
    #     if x + 1 > self.__size():
    #         for _ in range(x + 1 - self.__size()):
    #             self.__stackdata.appendleft(self.generateStackVar())
    #
    #     a = self.__stackdata[self.__size() - 1]
    #     self.__stackdata[self.__size() - 1] = self.__stackdata[self.__size() - 1 - x]
    #     self.__stackdata[self.__size() - 1 - x] = a

    # def dupx(self, x:int):
    #     if x < 1 or 16 < x:
    #         raise DevelopmentErorr()
    #
    #     if x > self.__size():
    #         for _ in range(x - self.__size()):
    #             self.__stackdata.appendleft(self.generateStackVar())
    #
    #     self.__stackdata.append(deepcopy(self.__stackdata[self.__size() - x]))

    def show_data(self):
        print('stack_id',id(self),len(self.__stackdata))
        for i in range(len(self.__stackdata))[::-1]:
            print("{}:{}".format(i, self.__stackdata[i]))


class Memory:
    # big-endian
    def __init__(self, block_number=0, immediate_data=None, num_memory_var=0):
        # blockNumber will be VM object's member
        self.__blockNumber = block_number
        self.__immediate_data = [] if immediate_data is None else immediate_data
        self.__numMemoryVar = num_memory_var

    def duplicate(self, new_block_number: int=None):
        if new_block_number is None:
            new_block_number = self.__blockNumber
        return Memory(new_block_number, deepcopy(self.__immediate_data), self.__numMemoryVar)

    def __generateMemoryVar(self):
        self.__numMemoryVar += 1
        return BitVec256('memoryVar{}-{}'.format(self.__blockNumber, self.__numMemoryVar))

    def mstore(self, offset: BitVecNumRef, value: BitVecRef):
        if not isinstance(offset, BitVecNumRef) and not isinstance(offset, int):
            raise DevelopmentErorr('Does not support memory operations indexed by symbol variables.')

        offset = offset.as_long() if isinstance(offset, BitVecNumRef) else offset
        checkBitVecRef256(value)

        if offset + WORDBYTESIZE > len(self.__immediate_data):
            d = offset + WORDBYTESIZE - len(self.__immediate_data)
            self.__immediate_data.extend([zero8bit() for _ in range(d)])

        #  for dict
        #
        # for i in range(self.__size(), offset + WORDBYTESIZE):
        #     self.__memdata[str(i)] = zero8bit()
        #
        for i in range(WORDBYTESIZE):
            self.__immediate_data[offset + (WORDBYTESIZE - 1 - i)] = Extract(i * 8 + 7, i * 8, value)

    def mstore8(self, offset: BitVecNumRef, value:BitVecRef):
        if isinstance(offset, BitVecNumRef):
            offset = checkBitVecRef256(offset).as_long()
        elif not isinstance(offset, int):
            raise DevelopmentErorr('Does not support memory operations indexed by symbol variables.')


        #checkBitVecRef256(value)

        if offset >= len(self.__immediate_data):
            d = offset - len(self.__immediate_data) + 1
            self.__immediate_data.extend([zero8bit() for _ in range(d)])
        self.__immediate_data[offset] = simplify(Extract(7, 0, value))

    def mload(self, offset: BitVecNumRef):
        if type(checkBitVecRef256(offset)) is not BitVecNumRef:
            raise DevelopmentErorr('Does not support memory operations indexed by symbol variables.')

        offset = checkBitVecRef256(offset).as_long()
        if offset + WORDBYTESIZE > len(self.__immediate_data):
            # ~ index out of bounds ~
            # generate a symblolic variable
            newmemvar = self.__generateMemoryVar()
            d = offset + WORDBYTESIZE - len(self.__immediate_data)
            if d < WORDBYTESIZE:
                for i in range(d):
                    self.__immediate_data.append(Extract((d - i - 1) * 8 + 7, (d - i - 1) * 8, newmemvar))
                return simplify(Concat(self.__immediate_data[offset: WORDBYTESIZE+offset]))
            else:
                self.mstore(BitVecVal256(offset), newmemvar)
                return newmemvar

        else:
            return simplify(
                Concat(self.__immediate_data[offset: WORDBYTESIZE+offset]))


    def size(self):
        return len(self.__immediate_data)

    def get_one_byte(self, i: int):
        return self.__immediate_data[i] if i < len(self.__immediate_data) else BitVecVal(0, 8)

    def show_data(self):
        print(self.__immediate_data)


class MsgData(Memory):
    # use exec_env_num instead of block number
    def __generateMemoryVar(self):
        self.__numMemoryVar += 1
        return BitVec256('MsgData{}-{}'.format(self.__blockNumber, self.__numMemoryVar))

    def set_function_id(self, fid:BitVecRef = None):
        if isinstance(fid, str) and len(fid) == 8:
            fid = BitVecVal(int(fid, 16), 32)
        elif isinstance(fid, int):
            fid = BitVecVal(fid, 32)
        elif isinstance(fid, BitVecRef) and fid.size() == 32:
            pass
        elif fid is None:
            fid = BitVec('function_id', 32)
        else:
            raise SettingError('illegal function id given')

        for i in range(4):
            fragment = Extract(i*8+7, i*8, fid)
            self.mstore8(3-i, fragment)

    def set_arguments(self, num):
        offset = self.size()
        for i in range(num):
            self.mstore8(offset+i,BitVec('msg_data_'+str(i),8))


class Storage:
    def __init__(self, block_number=0, storage_data=None, num_storage_var=0):
        self.__block_number = block_number
        self.__storage_data = {} if storage_data is None else storage_data
        self.__num_storage_var = num_storage_var

    def __generate_storage_var(self, key):
        # self.__num_storage_var += 1
        return BitVec256('storageVar_key='+str(key))

    def sload(self, key: BitVecRef) -> BitVecRef:
        key = str(checkBitVecRef256(key))
        if key in self.__storage_data.keys():
            return self.__storage_data[key]
        else:
            newvar = self.__generate_storage_var(key)
            self.__storage_data[key] = newvar
            return newvar

    def sstore(self, key: BitVecRef, value: BitVecRef):
        checkBitVecRef256(key)
        checkBitVecRef256(value)
        # # concrete value
        # if type(key) == BitVecNumRef:
        #     key = key.as_long()
        # # symbolic variable
        # else:
        #     key = str(key)
        self.__storage_data[str(key)] = value

    def duplicate(self, new_block_number):
        return Storage(new_block_number, deepcopy(self.__storage_data), self.__num_storage_var)

    def show_data(self):
        for k,v in self.__storage_data.items():
            print('key={}, value={}'.format(k, v))

    def get_data(self):
        return self.__storage_data



class Returndata(Memory):
    pass



# TODO call data
class Calldata:
    pass


class Account:
    def __init__(self, bytecode: str,
                 account_num: int,
                 balance: BitVecRef = None,
                 nonce=0):
        self.bytecode = bytecode
        self.codesize = lambda: len(bytecode)
        self.account_num = account_num
        self.__balance = BitVec256('account_balance_{}'.format(self.account_num)) if balance is None else balance
        self.nonce = nonce
        self.I = None

    def get_account_num(self) -> int:
        return self.account_num

    def get_balance(self) -> BitVecRef:
        return self.__balance

    def get_bytecode(self) -> str:
        return self.bytecode


class WorldState:
    def __init__(self):
        self.execution_environments = []
        self.block_hashes = {}
        self.accounts = {}

    def add_account(self, bytecode:str, addr:BitVecRef = None) -> BitVecRef:
        # アカウント番号とAccount address生成
        new_num = len(self.accounts)
        new_addr = ZeroExt(96,BitVec('address{}'.format(new_num), 160)) if addr is None else addr

        # Account生成
        account = Account(bytecode, new_num)

        # アドレスとAccountインスタンスの対応をaccountsに保存
        self.accounts[str(new_addr)] = account

        return new_addr

    def get_account(self, addr: BitVecRef) -> Account:
        return self.accounts[addr]

    def get_account_num(self, addr:BitVecRef) -> int:
        return self.accounts[addr].get_account_num()

    # def generate_execution_environment(self):
    #     pass
    '''
     IH= {
            'coinbase': BitVec('coinbase_{}'.format(eenum), 256),
            'timestamp': BitVec('timestamp_{}'.format(eenum), 256),
            'number': BitVec('blocknumber_{}'.format(eenum), 256),
            'difficulty': BitVec('difficulty_{}'.format(eenum), 256),
            'gaslimit': BitVec('_{}'.format(eenum), 256)
        }
    '''


class BlockHeader:
    def __init__(self,
                 Hi:BitVecRef = None,
                 Hp:BitVecRef = None,
                 Hc:BitVecRef = None,
                 Hs:BitVecRef = None,
                 Hd:BitVecRef = None,
                 Hl:BitVecRef = None):
        # self.__block_id = 'tmp{}'.format(int(random()*10**6)%10**6) if Hi is None else str(Hi)
        self.__block_number = BitVec256('blocknumber_current_block') if Hi is None else Hi
        self.__parent_hash = BitVec256('parent_hash_'+str(self.get_block_number())) if Hp is None else Hp
        self.__beneficiary = BitVec256('beneficiary_'+str(self.get_block_number())) if Hc is None else Hc
        self.__timestamp = BitVec256('timestamp_'+str(self.get_block_number())) if Hs is None else Hs
        self.__difficulty = BitVec256('difficulty_'+str(self.get_block_number())) if Hd is None else Hd
        self.__gaslimit = BitVec256('gaslimit_'+str(self.get_block_number())) if Hl is None else Hl

    def get_parent_hash(self) -> BitVecRef:
        return self.__parent_hash

    def get_block_number(self) -> BitVecRef:
        return self.__block_number

    def get_beneficiary(self) -> BitVecRef:
        return self.__beneficiary

    def get_timestamp(self) -> BitVecRef:
        return self.__timestamp

    def get_difficulty(self) -> BitVecRef:
        return self.__difficulty

    def get_gaslimit(self) -> BitVecRef:
        return self.__gaslimit



class ExecutionEnvironment:
    def __init__(self,
                 exec_env_id=None,
                 Ib: str='',
                 Ia:BitVecRef = None,
                 Io:BitVecRef = None,
                 Ip:BitVecRef = None,
                 Id:BitVecRef = None,
                 Is:BitVecRef = None,
                 Iv:BitVecRef = None,
                 IH:dict = None,
                 Ie:int = 0,
                 Iw:bool = True):
        self.__exec_env_id = id(self) if exec_env_id is None else exec_env_id
        self.this_address = BitVec256('Ia_{}'.format(self.__exec_env_id)) if Ia is None else Ia
        self.tx_originator = BitVec256('Io_{}'.format(self.__exec_env_id)) if Io is None else Io
        self.gasprice = BitVec256('Ip_{}'.format(self.__exec_env_id)) if Ip is None else Ip
        self.msg_data = MsgData(self.__exec_env_id) if Id is None else Id
        self.msg_sender = BitVec256('Is_{}'.format(self.__exec_env_id)) if Is is None else Is
        self.msg_value = BitVec256('Iv_{}'.format(self.__exec_env_id)) if Iv is None else Iv
        # TODO
        self.this_code = BitVec256('Ib_{}'.format(self.__exec_env_id)) if Ib is None else Ib
        self.block_header = BlockHeader() if IH is None else IH # TODO: blockheader IH
        self.depth_of_call = Ie
        self.permission_to_change_state = Iw
        #self.accounts = []
    # about Iw: https://ethereum.stackexchange.com/questions/49210/execution-environment-variables-iw-and-ie
    # def add_account(self,code: str):
    #     self.accounts.append(Account())

    def get_exec_env_id(self) -> int:
        return self.__exec_env_id

    def get_block_header(self) -> BlockHeader:
        return self.block_header

    def get_code(self) -> str:
        return self.this_code

    def get_msg_data(self) -> MsgData:
        return self.msg_data

    def show_all(self):
        print(self.this_address,self.tx_originator,self.gasprice,
              self.msg_data,self.msg_sender,self.msg_value,self.this_code,self.block_header,
              self.depth_of_call,self.permission_to_change_state)


class MachineState:
    def __init__(self,
        pc=0,
        memory=None,
        stack=None,
        storage=None,
        gas = None,
        retOffset = -1,
        retLength = -1,
        balance = None,
        returndata=None
        # calldata=Calldata()
        ):
        self.pc = pc
        self.memory = Memory() if memory is None else memory
        self.stack = Stack() if stack is None else stack
        self.storage = Storage() if storage is None else storage
        self.gas = BitVec256('gas_available{}'.format(id(self))) if gas is None else gas
        self.retOffset = retOffset
        self.retLength = retLength
        self.balance = BitVec256('default_balance') if balance is None else balance
        self.returndata = Returndata() if returndata is None else returndata

        # self.returndata = returndata
        # self.calldata = calldata

    def duplicate(self, new_block_number):
        return MachineState(
            self.pc,
            self.memory.duplicate(new_block_number),
            self.stack.duplicate(new_block_number),
            self.storage.duplicate(new_block_number),
            retOffset=self.retOffset,
            retLength=self.retLength,
            balance=self.balance,
            returndata=self.returndata.duplicate(new_block_number)
        )

    def get_pc(self):
        return self.pc

    def set_pc(self, pc: int):
        self.pc = pc

    def get_memory(self) -> Memory:
        return self.memory

    def get_stack(self) -> Stack:
        return self.stack

    def set_memory(self, memory:Memory):
        self.memory = memory

    def set_stack(self, stack:Stack):
        self.stack = stack

    def set_storage(self, storage:Storage):
        self.storage = storage

    def get_storage(self):
        return self.storage

    def get_gas(self) -> BitVecRef:
        return self.gas

    def set_gas(self, _gas):
        self.gas = _gas

    def set_retOffset(self, retOffset):
        self.retOffset = retOffset

    def get_retOffset(self) -> int:
        return self.retOffset

    def set_retLength(self, retLength):
        self.retLength = retLength

    def get_retLength(self) -> int:
        return self.retLength

    def get_return_data(self) -> Returndata:
        return self.returndata

    def set_return_data(self, returndate: Returndata):
        self.returndata = returndate

    def get_balance(self):
        return self.balance

    def set_balance(self, balance):
        self.balance = balance

    def show_all(self):
        print('----stack----')
        self.stack.show_data()
        print('----memory---')
        self.memory.show_data()
        print('----storage--')
        self.storage.show_data()
        print('----pc-------')
        print(self.get_pc())
        print('----gas------')
        print(self.gas)

# for type annotation in methods of BasicBlock
class BasicBlock:
    pass

class BasicBlock:
    def __init__(self,
                 #account_number: int,  # どのコントラクトのブロックか
                 block_number: int,
                 machine_state: MachineState = None,
                 exec_env: ExecutionEnvironment = None,
                 mnemonics: list = None,
                 path_condition = True,
                 cond_exp_for_JUMP = False,
                 dfs_stack=None,
                 call_stack=None,
                 jumpdest=-1,
                 path_location: list = None,
                 block_state: set = None,
                 depth: int = 0,
                 ):

        #self.account_number = account_number
        self.block_number = block_number
        self.__machine_state = MachineState() if machine_state is None else machine_state
        # TODO
        #self.__exec_env = ExecutionEnvironment(account_number) if exec_env is None else exec_env
        self.__exec_env = ExecutionEnvironment() if exec_env is None else exec_env
        self.mnemonics = [] if mnemonics is None else mnemonics
        self.path_condition = path_condition
        self.cond_exp_for_JUMP = cond_exp_for_JUMP
        self.dfs_stack = [] if dfs_stack is None else dfs_stack
        self.call_stack = [] if call_stack is None else call_stack
        self.__jumpdest = jumpdest
        self.jumpflag = False
        self.path_location = None if path_location is None else path_location
        self.block_state = [RUNNING] if block_state is None else block_state
        self.depth = depth


    def get_block_number(self):
        return self.block_number

    def add_mnemonic(self, numaddedbyte: int, mnemonic: str):
        self.mnemonics.append((self.__machine_state.get_pc(), mnemonic))

    def get_mnemonic_as_str(self):
        retstr = ''
        for i,op  in self.mnemonics:
            retstr += '0x{0:04x} '.format(i) + op + '\\l'
            if op == 'STOP' or op == 'INVALID' or op == 'RETURN' or op == 'REVERT':
                retstr += 'path condition: ' + str(
                    simplify(self.path_condition) if isinstance(self.path_condition, ExprRef)
                    else self.path_condition
                ) + '\\n'
        return retstr

    def duplicate(self,
                  #account_number: int,
                  new_block_number: int,
                  machine_state:MachineState = None,
                  exec_env:ExecutionEnvironment = None,
                  dfs_stack = None) -> BasicBlock:
        return BasicBlock(block_number=new_block_number,
                          machine_state=self.__machine_state.duplicate(new_block_number) if machine_state is None else machine_state,
                          # TODO 不変なのでコピーする必要はないはず
                          exec_env=self.__exec_env if exec_env is None else exec_env,
                          # deepcopy(self.mnemonics),
                          path_condition=deepcopy(self.path_condition),
                          cond_exp_for_JUMP=deepcopy(self.cond_exp_for_JUMP),
                          # TODO check 1
                          dfs_stack=copy(self.dfs_stack) if dfs_stack is None else dfs_stack,
                          call_stack=copy(self.call_stack),
                          path_location=self.path_condition,
                          block_state=copy(self.block_state),
                          depth=self.depth
                          )

    def inherit(self,
                new_block_number: int,
                jflag: bool = False):
        block = self.duplicate(new_block_number=new_block_number)
        # When a new block is reached by jump
        if jflag:
            block.set_pc(self.get_jumpdest())
            block.jumpflag = True
        else:
            block.set_pc(block.get_pc()+1)
        #block.clean_mnemonics()
        return block

    def clean_mnemonics(self):
        self.mnemonics = []
        self.__jumpdest = -1

    def push_dfs_stack(self, block:BasicBlock):
        self.dfs_stack.append(block)

    def pop_dfs_stack(self) -> BasicBlock:
        b = self.dfs_stack.pop()
        return b

    def get_dfs_stack_size(self) -> int:
        return len(self.dfs_stack)

    def show_dfs_stack(self):
        print(self.dfs_stack)

    def push_call_stack(self, block:BasicBlock):
        self.call_stack.append(block)

    def pop_call_stack(self) -> BasicBlock:
        return self.call_stack.pop()

    def get_call_stack_size(self) -> int:
        return len(self.call_stack)

    def show_call_stack(self):
        print(self.call_stack)

    def set_pc(self, pc:int):
        self.__machine_state.set_pc(pc)

    def get_pc(self):
        return self.__machine_state.get_pc()

    def get_gas(self):
        return self.__machine_state.get_gas()

    def get_machine_state(self) -> MachineState:
        return self.__machine_state

    def get_exec_env(self) -> ExecutionEnvironment:
        return self.__exec_env

    def set_jumpdest(self, dest):
        if isinstance(dest,str):
            self.__jumpdest = int(dest, 16)
        elif isinstance(dest,BitVecNumRef):
            self.__jumpdest = dest.as_long()
        elif isinstance(dest,int):
            self.__jumpdest = dest
        else:
            raise DevelopmentErorr

    def get_jumpdest(self):
        return self.__jumpdest

    # VMが持つデータを取り出す(pc以外は参照として)
    # def extract_data(self):
    #     return self.machine_state.get_memory(),\
    #            self.machine_state.get_stack(),\
    #            self.__storage,\
    #            self.machine_state.get_pc()

    def add_constraint_to_path_condition(self, constraint: BoolRef):
        self.path_condition = simplify(And(self.path_condition, constraint))

    def get_path_condition(self) -> BoolRef:
        return self.path_condition

    def set_path_condition(self, condition: BoolRef):
        self.path_condition = condition

    def get_path_condition(self):
        return self.path_condition

    def set_cond_exp_for_JUMP(self, constraint):
        self.cond_exp_for_JUMP = constraint

    def get_cond_exp_for_JUMP(self):
        return self.cond_exp_for_JUMP

    def get_exec_env(self) -> ExecutionEnvironment:
        return self.__exec_env

    def get_machine_state(self) -> MachineState:
        return self.__machine_state

    def add_block_state(self, state: str):
        self.block_state.append(state)

    def get_block_state(self) -> list:
        return self.block_state

    def get_depth(self):
        return self.depth


