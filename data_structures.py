from collections import deque
from copy import deepcopy
from z3 import BitVec, BitVecVal, BitVecRef, Concat, Extract, simplify
from utils import checkBitVecRef256

WORDBITSIZE = 256
WORDBYTESIZE = WORDBITSIZE // 8


class Stack():
    # def __init__(self, blockNumber=0, stdata=deque(), numStackVar=0):
    # def __init__(self, blockNumber=0, stdata_and_numStackVar=(deque(), 0)):
    # TODO refacturing field name
    def __init__(self, blockNumber=0, stdata=deque(), numStackVar=0):
        # blockNumber will be VM object's member
        self.blockNumber = blockNumber
        self.stackdata = stdata
        self.numStackVar = numStackVar

    size = lambda self: len(self.stackdata)

    def duplicate(self, new_block_number:int):
        return Stack(new_block_number, deepcopy(self.stackdata), self.numStackVar)

    def generateStackVar(self):
        self.numStackVar += 1
        return BitVec(
            'stackVar{}-{}'.format(self.blockNumber, self.numStackVar),
            256)

    def push(self, w:BitVecRef):
        if self.size() < 1023:
            self.stackdata.append(checkBitVecRef256(w))
        else:
            # TODO stack limit reached 1024
            pass

    def pop(self) -> BitVecRef:
        if self.size() >= 1:
            return checkBitVecRef256(self.stackdata.pop())
        else:
            # generate a symbolic variable
            # TODO this may cause stack underflow
            return self.generateStackVar()

    def swapx(self, x:int):
        if x < 1 or 16 < x:
            # TODO error due to misshandle opcode
            pass

        if x + 1 > self.size():
            for _ in range(x + 1 - self.size()):
                self.stackdata.appendleft(self.generateStackVar)

        a = self.stackdata[self.size() - 1]
        self.stackdata[self.size() - 1] = self.stackdata[self.size() - 1 - x]
        self.stackdata[self.size() - 1 - x] = a

    def dupx(self, x:int):
        if x < 1 or 16 < x:
            # TODO error due to misshandle opcode
            pass

        if x > self.size():
            for _ in range(x - self.size()):
                self.stackdata.appendleft(self.generateStackVar)

        self.stackdata.append(self.stackdata[self.size() - x])


class Memory():
    def __init__(self, blockNumber=0, memdata=[], numMemoryVar=0):
        # blockNumber will be VM object's member
        self.blockNumber = blockNumber
        self.memdata = memdata
        self.size = lambda: len(self.memdata)
        self.numMemoryVar = numMemoryVar

    def generateMemoryVar(self):
        self.numMemoryVar += 1
        return BitVec(
            'memoryVar{}-{}'.format(self.blockNumber, self.numMemoryVar),
            256)

    def mstore(self, offset:int, value:BitVecRef):
        if offset + WORDBYTESIZE > self.size():
            d = offset + WORDBYTESIZE - self.size()
            self.memdata.extend([BitVecVal(0, 8) for _ in range(d)])

        for i in range(WORDBYTESIZE):
            self.memdata[offset+i] = Extract(i*8+7, i*8, checkBitVecRef256(value))


    # TODO mstore8
    def mstore8(self, value:BitVecRef):
        pass




    def mload(self, offset:int):
        if offset + WORDBYTESIZE > self.size():
            # ~ index out of bounds ~
            # generate a symblolic variable
            newmemvar = self.generateMemoryVar()
            self.mstore(offset, newmemvar)
            return newmemvar

        elif offset < 0:
            # TODO  index out of bounds
            pass
        else:
            return simplify(
                Concat(self.memdata[offset+WORDBYTESIZE:offset:-1]))

    def msize(self):
        return self.memsize

    # TODO generate copy


class Storage():
    def __init__(self, block_number, storage_data_and_num_storage_var=({}, 0)):
        self.block_number = block_number
        self.storage_data = storage_data_and_num_storage_var[0]
        self.num_storage_var = storage_data_and_num_storage_var[1]

    def generate_storage_var(self):
        self.num_storage_var += 1
        return BitVec(
            'storageVar{}-{}'.format(self.blockNumber, self.num_storage_var),
            256)

    def sload(self, key):
        if key in self.storage_data.keys():
            return self.storage_data[key]
        else:
            newvar = self.generate_storage_var()
            self.storage_data[key] = newvar
            return newvar

    def sstore(self, key, value):
        self.storage_data[key] = value
    # TODO generate copy


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
        self.cond_exps_to_reach_this = cond_exps_to_reach_this
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
    def __init__(self, eenum:int, Ia:BitVec, Ip:BitVec, Id:BitVec, Is:BitVec, Iv:BitVec, Ib:BitVec, IH:dict):
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
    print(m.memdata)

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
        sys.stdout.write(str(s.stackdata[i]))
        sys.stdout.write(' ')

    s2 = s.duplicate(1)
    for i in range(s2.size()):
        sys.stdout.write('i={} '.format(i))
        sys.stdout.write(str(simplify(s2.stackdata[i] * BitVecVal(2, 256) / BitVecVal(2, 256))))
        print()



