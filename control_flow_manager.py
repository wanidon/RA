from data_structures import BasicBlock, ExecutionEnvironment, Account
from exceptions import DevelopmentErorr
from z3 import Solver, unsat, Not, BitVecRef
from collections import defaultdict

class ControlFlowManager:
    def __init__(self):
        self.__cfmanager_id = id(self)
        self.basic_blocks = []
        self.__edges = defaultdict(list)
        self.__CFG_name = "CFG_{}".format(self.__cfmanager_id)
        # self.__call_stack = []
        # self.__dfs_stack = []
        # exec_id -> index of bytecode -> bool
        self.visited_address = defaultdict(lambda: defaultdict(lambda : False))
        self.processing_block: BasicBlock = None

    # def convert_bytecode_to_account(self, bytecode) -> Account:
    #     Account()

    def get_cfmanager_id(self) -> int:
        return self.__cfmanager_id

    def get_exec_id(self):
        return id(self.processing_block.__exec_env)

    def push_to_call_stack(self, block: BasicBlock):
        self.processing_block.push_call_stack(block)

    def pop_from_call_stack(self) -> BasicBlock:
        return self.processing_block.pop_call_stack()

    def push_to_dfs_stack(self, block: BasicBlock):
        self.processing_block.push_dfs_stack(block)

    def pop_from_dfs_stack(self) -> BasicBlock:
        return self.processing_block.pop_dfs_stack()

    def is_dfs_stack_empty(self):
        return self.processing_block.get_dfs_stack_size() == 0

    def is_call_stack_empty(self):
        return self.processing_block.get_call_stack_size() == 0



    def add_mnemonic(self, mnemonic: str):
        self.processing_block.mnemonics.append([self.processing_block.get_pc(), mnemonic])

    # def set_jump_dest(self, dest):
    #     self.processing_block.set_jumpdest(dest)
    def add_immediatevalue(self, iv: str):
        self.processing_block.mnemonics[-1][1] += ' 0x' + iv

    def get_num_basicblocks(self):
        return len(self.basic_blocks)

    def set_procesisng_block(self, block:BasicBlock):
        self.processing_block = block
        self.basic_blocks.append(block)

    def get_processing_block(self):
        return self.processing_block

    # ジャンプなしでブロック更新がある場合
    def inherit_from_processing_block(self, continuable: bool, jumpable: bool, condition):
        print(continuable, jumpable)
        s = Solver()
        s.push()

        if continuable:
            # 先にcontinuation_blockを生成することでブロック番号を若くする
            # Generate a continuation_block first to make the block number younger
            continuation_block = self.processing_block.inherit(len(self.basic_blocks), False)
            continuation_block.add_constraint_to_path_condition(Not(condition))
            # 到達不能の場合　または　到達済みの場合何もしない
            s.add(continuation_block.get_path_condition())
            if not s.check() == unsat or not\
                    self.visited_address[self.get_exec_id()][self.processing_block.get_pc()]:

                self.basic_blocks.append(continuation_block)
                self.__edges[self.processing_block].append(continuation_block)
                print('pc of conti block = ', continuation_block.get_pc())

            s.pop()



        if jumpable:
            jump_block = self.processing_block.inherit(
                new_block_number=len(self.basic_blocks),
                jflag=True)
            jump_block.add_constraint_to_path_condition(condition)
            s.add(jump_block.get_path_condition())
            if not s.check() == unsat or \
                    not self.visited_address[self.get_exec_id()][self.processing_block.get_pc()]:


                self.basic_blocks.append(jump_block)
                self.__edges[self.processing_block].append(jump_block)

                print('pc of jump block = ', jump_block.get_pc())



        if continuable:
            self.processing_block = continuation_block
            if jumpable:
                self.push_to_dfs_stack(jump_block)
        else:
            self.processing_block = jump_block

        return self.processing_block

    # # ジャンプのみでブロック更新がある場合
    # def jump_from_processing_block(self):
    #     jump_block = self.processing_block.inherit(len(self.basic_blocks), True)
    #     self.basic_blocks.append(jump_block)
    #     self.__edges[self.processing_block].append(jump_block)




    def search_existing_block(self,
                              exec_id:int,
                              pc:int):
        for block in self.basic_blocks:
            if block.get_machine_state().get_pc()==pc \
                    and block.get_exec_env().get_exec_env_id() == exec_id\
                    and block != self.processing_block:
                import sys
                print('search_existing_block!',self.processing_block,block)
                self.add_edge(self.processing_block, block)
                self.processing_block = block
                return
        return

    def external_call(self,
                      # account_number:int,
                      exec_env:ExecutionEnvironment,
                      condition=True
                      #machine_state:MachineState=None
                      ):

        continuation_block = self.processing_block.inherit(len(self.basic_blocks), False)
        self.add_basic_block(continuation_block)
        self.push_to_call_stack(continuation_block)



        external_block = self.processing_block.duplicate(
            # account_number=account_number,
            new_block_number=len(self.basic_blocks),
            #machine_state=machine_state,
            exec_env=exec_env,
            dfs_stack=[])
        external_block.set_pc(0)
        external_block.add_constraint_to_path_condition(condition)

        # # TODO manage visited address
        # if not self.visited_address[exec_env.get_exec_env_id()][external_block.get_pc()]:


        self.basic_blocks.append(external_block)
        self.__edges[self.processing_block].append(external_block)

        print('pc of external block = ', external_block.get_pc())






        self.processing_block = external_block

        return self.processing_block




    def rollback_from_dfs_stack(self):
        if self.is_dfs_stack_empty():
            raise DevelopmentErorr('call stack is empty')
        else:
            block = self.pop_from_dfs_stack()
            self.processing_block = block
            print(block)
            return block

    def rollback_from_call_stack(self):
        if self.is_call_stack_empty():
            raise DevelopmentErorr('call stack is empty')
        else:
            block = self.pop_from_call_stack()
            self.add_edge(self.processing_block,block)
            block.add_constraint_to_path_condition(self.processing_block.get_path_condition())
            return block


    def add_basic_block(self, basic_block: BasicBlock):
        self.basic_blocks.append(basic_block)

    def add_visited_block(self, basic_block: BasicBlock):
        self.__visited_blocks.append(basic_block)

    def get_basic_blocks(self):
        return self.basic_blocks

    def get_visited_blocks(self):
        return self.__visited_blocks

    def add_edge(self, origin: BasicBlock, dest: BasicBlock):
        if origin in self.__edges[dest]:
            import sys
            sys.stderr.write('looooooooooooooooooooooooooop')
            print()
        self.__edges[origin].append(dest)

    def get_dest_blocks(self, origin: BasicBlock):
        return self.__edges[origin]

    def get_CFG_name(self):
        return self.__CFG_name

    def extract_mnemonics(self, block: BasicBlock):
        node = block.get_block_number()
        nodes = set()
        nodes.add(node)
        mnemonics = {node:str(block.get_mnemonic_as_str())}
        jumpdests = {node:block.get_jumpdest()}
        edges = ''
        dests = self.get_dest_blocks(block)
        for d in dests:
            if d==block:
                continue
            dn = d.get_block_number()
            nodes.add(dn)
            edges += 'block' + str(node) + ' -> ' + 'block' + str(dn) + '\n'

            m, e, n, j = self.extract_mnemonics(d)

            mnemonics.update(m)
            edges += e
            nodes |= n
            jumpdests.update(j)

        return (mnemonics,edges,nodes,jumpdests)

    def gen_CFG(self):
        root = self.basic_blocks[0]
        mnemonics, edges, nodes, jumpdests = self.extract_mnemonics(root)
        nodedefine = ''
        for n in nodes:
            nodedefine += 'block' + str(n) + '[shape=box,label = "'
            nodedefine += mnemonics[n]
            if jumpdests[n] != -1:
                nodedefine += 'jumpdest: {0:04x}\n'.format(jumpdests[n])
            nodedefine += '"];\n'

        cfg = 'digraph ' + self.get_CFG_name() + ' {\n'
        cfg += nodedefine
        cfg += edges
        cfg += '}'

        return (self.get_CFG_name(), cfg)

    def show_all(self):
        print('----CFG name and number--')
        print(self.get_CFG_name(),self.get_cfmanager_id())
        print('----basic blocks-')
        print(self.basic_blocks)
        print('----visited address-')
        print(self.visited_address)
        print('----edges----')
        print(self.__edges)

