# coding:utf-8
from collections import deque
from copy import deepcopy
from z3 import BitVecRef, BitVecNumRef, Concat, Extract, simplify
from utils import BitVec256, BitVecVal256, zero8bit, checkBitVecRef256
from exceptions import DevelopmentErorr
from collections import defaultdict

WORDBITSIZE = 256
WORDBYTESIZE = WORDBITSIZE // 8


class Stack:
    # def __init__(self, blockNumber=0, stdata=deque(), numStackVar=0):
    # def __init__(self, blockNumber=0, stdata_and_numStackVar=(deque(), 0)):
    # TODO refacturing field name
    def __init__(self, block_number=0, stdata=deque(), num_stack_var=0):
        # blockNumber will be VM object's member
        self.__blockNumber = block_number
        self.__stackdata = stdata
        self.__numStackVar = num_stack_var

    size = lambda self: len(self.__stackdata)

    def duplicate(self, new_block_number:int):
        return Stack(new_block_number, deepcopy(self.__stackdata), self.__numStackVar)

    def generateStackVar(self) -> BitVecRef:
        self.__numStackVar += 1
        return BitVec256('stackVar{}-{}'.format(self.__blockNumber, self.__numStackVar))

    def push(self, w:BitVecRef):
        if self.size() < 1023:
            self.__stackdata.append(checkBitVecRef256(w))
        else:
            # TODO stack limit reached 1024
            pass

    def pop(self) -> BitVecRef:
        if self.size() >= 1:
            return checkBitVecRef256(self.__stackdata.pop())
        else:
            # generate a symbolic variable
            # TODO this may cause stack underflow
            return self.generateStackVar()

    def swapx(self, x:int):
        if x < 1 or 16 < x:
            raise DevelopmentErorr()

        if x + 1 > self.size():
            for _ in range(x + 1 - self.size()):
                self.__stackdata.appendleft(self.generateStackVar())

        a = self.__stackdata[self.size() - 1]
        self.__stackdata[self.size() - 1] = self.__stackdata[self.size() - 1 - x]
        self.__stackdata[self.size() - 1 - x] = a

    def dupx(self, x:int):
        if x < 1 or 16 < x:
            raise DevelopmentErorr()

        if x > self.size():
            for _ in range(x - self.size()):
                self.__stackdata.appendleft(self.generateStackVar())

        self.__stackdata.append(self.__stackdata[self.size() - x])

    def show_data(self):
        for i in range(self.size())[::-1]:
            print("{}:{}".format(i, self.__stackdata[i]))


class Memory:
    # big-endian
    def __init__(self, block_number=0, num_mmory_var=0, immediate_data=[]):
        # blockNumber will be VM object's member
        self.__blockNumber = block_number
        self.__immediate_data = immediate_data
        self.__size = lambda: len(self.__immediate_data)
        self.__numMemoryVar = num_memory_var

    def __generateMemoryVar(self):
        self.__numMemoryVar += 1
        return BitVec256('memoryVar{}-{}'.format(self.__blockNumber, self.__numMemoryVar))

    def mstore(self, offset: BitVecNumRef, value: BitVecRef):
        if type(offset) != BitVecNumRef:
            raise DevelopmentErorr('Does not support memory operations indexed by symbolic variables.')

        offset = checkBitVecRef256(offset).as_long()
        checkBitVecRef256(value)

        if offset + WORDBYTESIZE > self.__size():
            d = offset + WORDBYTESIZE - self.__size()
            self.__immediate_data.extend([zero8bit() for _ in range(d)])

        #  for dict
        #
        # for i in range(self.__size(), offset + WORDBYTESIZE):
        #     self.__memdata[str(i)] = zero8bit()
        #
        for i in range(WORDBYTESIZE):
            self.__immediate_data[offset + (WORDBYTESIZE - 1 - i)] = Extract(i * 8 + 7, i * 8, value)

    def mstore8(self, offset: BitVecNumRef, value:BitVecRef):
        if type(offset) != BitVecNumRef:
            raise DevelopmentErorr('Does not support memory operations indexed by symbolic variables.')

        offset = checkBitVecRef256(offset).as_long()
        checkBitVecRef256(value)

        if offset >= self.__size():
            d = offset - self.__size() + 1
            self.__immediate_data.extend([zero8bit() for _ in range(d)])

        self.__immediate_data[offset] = simplify(Extract(7, 0, value))

    def mload(self, offset: BitVecNumRef):
        if type(checkBitVecRef256(offset)) is not BitVecNumRef:
            raise DevelopmentErorr('Does not support memory operations indexed by symbolic variables.')

        offset = checkBitVecRef256(offset).as_long()
        if offset + WORDBYTESIZE > self.__size():
            # ~ index out of bounds ~
            # generate a symblolic variable
            newmemvar = self.__generateMemoryVar()
            d = offset + WORDBYTESIZE - self.__size()
            if d < WORDBYTESIZE:
                for i in range(d):
                    self.__immediate_data.append(Extract((d - i - 1) * 8 + 7, (d - i - 1) * 8, newmemvar))
                return simplify(Concat(self.__immediate_data[offset: WORDBYTESIZE+offset]))
            else:
                self.mstore(BitVecVal256(offset), newmemvar)
                return newmemvar

        elif offset < 0:
            # TODO  index out of bounds
            pass
        else:
            return simplify(
                Concat(self.__immediate_data[offset: WORDBYTESIZE+offset]))

    def msize(self):
        return self.__size()

    def duplicate(self, block_number):
        return Memory(block_number, deepcopy(self.__numMemoryVar), deepcopy(self.__immediate_data))

    def show_data(self):
        print(self.__immediate_data)


class Storage:
    def __init__(self, block_number=0, storage_data={}, num_storage_var=0):
        self.__block_number = block_number
        self.__storage_data = storage_data
        self.__num_storage_var = num_storage_var

    def __generate_storage_var(self):
        self.__num_storage_var += 1
        return BitVec256('storageVar{}-{}'.format(self.__block_number, self.__num_storage_var))

    def sload(self, key: BitVecRef) -> BitVecRef:
        key = str(checkBitVecRef256(key))
        if key in self.__storage_data.keys():
            return self.__storage_data[key]
        else:
            newvar = self.__generate_storage_var()
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

    def duplicate(self, block_number):
        return Storage(block_number, deepcopy(self.__storage_data), self.__num_storage_var)

    def show_data(self):
        for k,v in self.__storage_data.items():
            print('key={}, value={}'.format(k, v))


# TODO return data
class Returndata():
    pass
# TODO call data
class Calldata:
    pass


class System_state:
    def __init__(self):
        self.execution_environments = []
        self.block_hashes = {}

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



class Execution_environment:
    def __init__(self, eenum:int, Ia:BitVec256, Ip:BitVec256, Id:BitVec256, Is:BitVec256, Iv:BitVec256, Ib:BitVec256, IH:dict):
        self.eenum = eenum
        self.this_address = Ia
        self.gasprice = Ip
        self.msg_data = Id
        self.msg_caller = Is
        self.msg_value = Iv
        self.this_code = Ib
        self.block_header = IH
        self.accounts = []

    def add_account(self,code: str):
        self.accounts.append(Account())


class Execution_state:
    def __init__(self,
        pc=0,
        memory=Memory(),
        stack=Stack(),
        storage=Storage(0),
        returndata=Returndata(), 
        calldata=Calldata()
        ):
        self.pc = pc
        self.memory = memory
        self.stack = stack
        self.storage = storage
        self.returndata = returndata
        self.calldata = calldata

class BasicBlock:
    def __init__(self, account_number : int, block_number: int, execution_state: Execution_state=None, cond_exps_to_reach_this: list=None, cond_exp_for_JUMPI:bool = False, ):
        self.__account_number = account_number
        self.__block_number = block_number
        self.__execution_state = Execution_state() if execution_state is None else execution_state
        self.mnemonics = []
        self.path_conditions = [True] if cond_exps_to_reach_this is None else cond_exps_to_reach_this
        self.cond_exp_for_JUMPI = cond_exp_for_JUMPI

    def add_mnemonic(self, numbyte: int, mnemonic: str):
        self.mnemonics.append((numbyte, mnemonic))

    def get_mnemonic(self):
        return self.mnemonics



class CFG_manager:
    def __init__(self, eenum:int):
        self.__eenum = eenum
        self.__basic_blocks = []
        self.__visited_blocks = []
        self.__edges = defaultdict([])
        self.__CFG_name = "CFG_{}".format(self.eenum)

    def add_basic_block(self, basic_block : BasicBlock):
        self.__basic_blocks.append(basic_block)

    def add_visited_block(self, basic_block : BasicBlock):
        self.__visited_blocks.append(basic_block)

    def get_basic_blocks(self):
        return self.__basic_blocks

    def get_visited_blocks(self):
        return self.__visited_blocks

    def add_edge(self, origin: BasicBlock, dest: BasicBlock):
        self.__edges[origin].append(dest)

    def get_dest_block(self, origin: BasicBlock):
        return self.__edges[origin]

    def get_CFG_name(self):
        return self.__CFG_name

class Account:
    def __init__(self, code: str, account_num: int):
        self.code = code
        self.codesize = lambda:len(code)
        self.account_num = account_num
        self.balance = BitVec256('account_balance_{}'.format(self.account_num))







# if __name__ == '__main__':
#     m = Memory()
#     m.mstore(0,BitVec("hoge",256))
#     print(m.mload(0))
#     print(m.mload(45))
#     print(m.__memdata)
#
#     s = Stack()
#     t = BitVecVal(100+ 2**1024-1,256)
#     print(t)
#     s.push(t)
#     print(s.pop())
#     print(s.pop())
#     s.push(BitVecVal(1,256))
#     s.push(BitVecVal(2,256))
#     s.push(BitVec("hoge",256))
#     s.push(BitVecVal(4,256))
#     s.swapx(1)
#     s.dupx(1)
#     s.dupx(5)
#     s.swapx(4)
#     import sys
#     for i in range(s.size()):
#         sys.stdout.write(str(s.__stackdata[i]))
#         sys.stdout.write(' ')
#
#     s2 = s.duplicate(1)
#     for i in range(s2.size()):
#         sys.stdout.write('i={} '.format(i))
#         sys.stdout.write(str(simplify(s2.__stackdata[i] * BitVecVal(2, 256) / BitVecVal(2, 256))))
#         print()
#
#
#
