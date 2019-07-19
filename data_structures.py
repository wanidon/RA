from collections import deque
from copy import deepcopy
from z3 import BitVecRef, BitVecNumRef, Concat, Extract, simplify
from utils import BitVec256, BitVecVal256, zero8bit, checkBitVecRef256
from exceptions import DevelopmentErorr

WORDBITSIZE = 256
WORDBYTESIZE = WORDBITSIZE // 8


class Stack():
    # def __init__(self, blockNumber=0, stdata=deque(), numStackVar=0):
    # def __init__(self, blockNumber=0, stdata_and_numStackVar=(deque(), 0)):
    # TODO refacturing field name
    def __init__(self, blockNumber=0, stdata=deque(), numStackVar=0):
        # blockNumber will be VM object's member
        self.__blockNumber = blockNumber
        self.__stackdata = stdata
        self.__numStackVar = numStackVar

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


class Memory():
    def __init__(self, blockNumber=0, memdata=[], numMemoryVar=0):
        # blockNumber will be VM object's member
        self.__blockNumber = blockNumber
        self.__memdata = memdata
        self.__size = lambda: len(self.__memdata)
        self.__numMemoryVar = numMemoryVar

    def __generateMemoryVar(self):
        self.__numMemoryVar += 1
        return BitVec256('memoryVar{}-{}'.format(self.__blockNumber, self.__numMemoryVar))

    def mstore(self, offset:int, value:BitVecRef):
        if offset + WORDBYTESIZE > self.__size():
            d = offset + WORDBYTESIZE - self.__size()
            self.__memdata.extend([zero8bit() for _ in range(d)])

        for i in range(WORDBYTESIZE):
            self.__memdata[offset + i] = Extract(i * 8 + 7, i * 8, checkBitVecRef256(value))


    # TODO mstore8
    def mstore8(self, value:BitVecRef):
        pass




    def mload(self, offset:int):
        if offset + WORDBYTESIZE > self.__size():
            # ~ index out of bounds ~
            # generate a symblolic variable
            newmemvar = self.__generateMemoryVar()
            self.mstore(offset, newmemvar)
            return newmemvar

        elif offset < 0:
            # TODO  index out of bounds
            pass
        else:
            return simplify(
                Concat(self.__memdata[offset + WORDBYTESIZE:offset:-1]))

    def msize(self):
        return self.__size()

    # TODO generate copy


class Storage():
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
class Calldata:
    pass
class Node:
    def __init__(self, node_number: int, ond_exp_for_JUMPI=False, cond_exp_to_reach_this=[]):
        self.node_number = node_number
        self.execution_state = None
        self.mnemonics = []
        self.path_conditions = cond_exps_to_reach_this
        self.cond_exp_for_JUMPI = cond_exp_for_JUMPI


class System_state:
    def __init__(self):
        self.execution_environments = []
        self.block_hashes = {}

    def generate_execution_environment(self):
        pass
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

class CFG_manager:
    def __init__(self, eenum:int):
        self.eenum = eenum
        self.Nodes = []
        self.edges = {}
        self.CFG_filename = "CFG_{}".format(self.eenum)


class Account:
    def __init__(self, code: str, account_num: int):
        self.code = code
        self.codesize = lambda:len(code)
        self.account_num = account_num
        self.balance = BitVec('account_balance_{}'.format(self.account_num), 256)







if __name__ == '__main__':
    m = Memory()
    m.mstore(0,BitVec("hoge",256))
    print(m.mload(0))
    print(m.mload(45))
    print(m.__memdata)

    s = Stack()
    t = BitVecVal(100+ 2**1024-1,256)
    print(t)
    s.push(t)
    print(s.pop())
    print(s.pop())
    s.push(BitVecVal(1,256))
    s.push(BitVecVal(2,256))
    s.push(BitVec("hoge",256))
    s.push(BitVecVal(4,256))
    s.swapx(1)
    s.dupx(1)
    s.dupx(5)
    s.swapx(4)
    import sys
    for i in range(s.size()):
        sys.stdout.write(str(s.__stackdata[i]))
        sys.stdout.write(' ')

    s2 = s.duplicate(1)
    for i in range(s2.size()):
        sys.stdout.write('i={} '.format(i))
        sys.stdout.write(str(simplify(s2.__stackdata[i] * BitVecVal(2, 256) / BitVecVal(2, 256))))
        print()



