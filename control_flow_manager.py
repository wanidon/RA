from data_structures import BasicBlock, ExecutionEnvironment, Memory, Stack
from exceptions import DevelopmentErorr
from z3 import Solver, unsat, Or, Not, BitVecRef, BoolRef, simplify,sat
from collections import defaultdict
from utils import dbgredmsg, solve_and_time
import time_measurement
from copy import deepcopy
from vulnerability_verifier import VulnerabilityVerifierAfterCall

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
        return self.processing_block.get_exec_env().get_exec_env_id()

    def push_to_call_stack(self, block: BasicBlock):
        self.processing_block.push_call_stack(block)

    def pop_from_call_stack(self) -> BasicBlock:
        return self.processing_block.pop_call_stack()

    def push_to_dfs_stack(self, block: BasicBlock):
        self.processing_block.push_dfs_stack(block)

    def pop_from_dfs_stack(self) -> BasicBlock:

        b=self.processing_block.pop_dfs_stack()
        return b

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

    def get_processing_block(self) -> BasicBlock:
        return self.processing_block

    def integrate_path_condition(self, constraint: BoolRef, integrated_block: BasicBlock):
        integrated_block.set_path_condition(
            simplify(Or(integrated_block.get_path_condition, constraint))
        )
        for dest in self.get_dest_blocks(integrated_block):
            self.integrate_path_condition(constraint, dest)

    def inherit_from_processing_block(self, continuable: bool, jumpable: bool, condition):
        # s = Solver()
        # s.push()
        if continuable:
            # 先にcontinuation_blockを生成することでブロック番号を若くする
            # Generate a continuation_block first to make the block number younger
            continuation_block = self.processing_block.inherit(len(self.basic_blocks), False)
            continuation_block.add_constraint_to_path_condition(Not(condition))
            # 到達不能の場合　または　到達済みの場合何もしない
            # nothing to do when unreachable or reached
            # s.add(continuation_block.get_path_condition())
            # st = time()
            # ck = s.check()
            # time_measurement.solving_time += time() - st
            if not self.visited_address[self.get_exec_id()][continuation_block.get_pc()]:
                # print('visited',
                #       ck,
                #       self.visited_address[self.get_exec_id()][continuation_block.get_pc()],
                #       self.get_processing_block().get_pc())
                self.basic_blocks.append(continuation_block)
                self.__edges[self.processing_block].append(continuation_block)
            else:
                continuable = False

            # s.pop()



        if jumpable:
            jump_block = self.processing_block.inherit(
                new_block_number=len(self.basic_blocks),
                jflag=True)
            jump_block.add_constraint_to_path_condition(condition)
            # s.add(jump_block.get_path_condition())
            #
            # st = time()
            # ck = s.check()
            # time_measurement.solving_time += time() - st
            if not self.visited_address[self.get_exec_id()][jump_block.get_pc()]:
                # print('visited,jumpable?',
                #       ck,
                #       self.visited_address[self.get_exec_id()][jump_block.get_pc()],
                #       self.get_processing_block().get_pc())
                # print('exec id=',self.get_exec_id())
                self.basic_blocks.append(jump_block)
                self.__edges[self.processing_block].append(jump_block)
            else:
                jumpable = False




        if continuable:
            self.processing_block = continuation_block
            if jumpable:
                self.push_to_dfs_stack(jump_block)

        elif jumpable:
            self.processing_block = jump_block
        else:
            # dbgredmsg(condition)
            # return False
            pass

        return self.processing_block

    # # ジャンプのみでブロック更新がある場合
    # def jump_from_processing_block(self):
    #     jump_block = self.processing_block.inherit(len(self.basic_blocks), True)
    #     self.basic_blocks.append(jump_block)
    #     self.__edges[self.processing_block].append(jump_block)

    # switch to block beginning with JUMPDEST
    def search_existing_block(self,
                              exec_id: int,
                              pc: int):
        for block in self.basic_blocks:
            if block.get_machine_state().get_pc() == pc \
                    and block.get_exec_env().get_exec_env_id() == exec_id\
                    and block != self.processing_block:
                return block
        return None


    def switch_block(self,
                      exec_id: int,
                      pc: int):
        block = self.get_processing_block().inherit(
            new_block_number=self.get_num_basicblocks()
        )
        self.add_edge(self.get_processing_block(), block)
        block.set_pc(block.get_pc()-1)
        self.set_procesisng_block(block)

    #廃止
    def switch_existing_block(self,
                              exec_id: int,
                              pc: int):
        block = self.search_existing_block(exec_id,pc)
        if block is not None:
            dbgredmsg('pre dfs stack size=',self.get_processing_block().get_dfs_stack_size())
            dbgredmsg(self.processing_block, block)
            self.add_edge(self.processing_block, block)
            self.set_procesisng_block(block)
            dbgredmsg('next dfs stack size=',self.get_processing_block().get_dfs_stack_size())
            return
        else:
            dbgredmsg('not found')

            # next_block = self.get_processing_block().inherit(
            #         new_block_number=self.get_num_basicblocks()
            #     )
            #
            # self.add_basic_block(next_block)
            # self.add_edge(self.get_processing_block(), next_block)
            # # next_block.set_pc(next_block.get_pc())
            # self.set_procesisng_block(next_block)

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


        new_block_number = len(self.basic_blocks)
        external_block = self.processing_block.duplicate(
            # account_number=account_number,
            new_block_number=new_block_number,
            exec_env=exec_env,
            dfs_stack=[])
        external_block.set_pc(0)
        external_block.get_machine_state().set_stack(Stack(block_number=new_block_number))
        external_block.get_machine_state().set_memory(Memory(block_number=new_block_number))
        external_block.add_constraint_to_path_condition(condition)

        # # TODO manage visited address
        # if not self.visited_address[exec_env.get_exec_env_id()][external_block.get_pc()]:


        self.basic_blocks.append(external_block)
        self.__edges[self.processing_block].append(external_block)







        self.processing_block = external_block

        return self.processing_block




    def rollback_from_dfs_stack(self):
        while not self.is_dfs_stack_empty():
            next_block = self.pop_from_dfs_stack()
            next_pc = next_block.get_pc()
            if self.visited_address[self.processing_block.get_exec_env().get_exec_env_id()][next_pc]:
                # for edge in self.__edges.values():
                #     while next_block in edge:
                #         edge.remove(next_block)
                #         print('deleted')
                continue
            else:
                self.set_procesisng_block(next_block)
                return next_block

        return False




    def rollback_from_call_stack(self, verifier:VulnerabilityVerifierAfterCall = None) -> BasicBlock:
        if self.is_call_stack_empty():
            return False
        else:
            # print('rollback from call stack')
            verifier.extract_data_with_callback(self.processing_block.get_path_condition(),
                                                self.processing_block.get_block_state(),
                                                self.processing_block.get_machine_state().get_storage(),
                                                self.processing_block.get_machine_state().get_balance(),
                                                self.processing_block.get_depth(),
                                                )
            return_block = self.pop_from_call_stack()
            self.add_edge(self.processing_block, return_block)
            return_block.add_constraint_to_path_condition(self.processing_block.get_path_condition())
            new_block_num = return_block.get_block_number()
            # return_block.get_machine_state().set_memory(
            #     self.processing_block.get_machine_state().get_memory().duplicate(new_block_num))
            # return_block.get_machine_state().set_stack(
            #     self.processing_block.get_machine_state().get_stack().duplicate(new_block_num))
            # print('storage:',id(self.processing_block.get_machine_state().get_storage()))
            # print(self.processing_block.get_machine_state().get_storage().get_data())
            # print('dup:')
            # print(self.processing_block.get_machine_state().get_storage().duplicate(new_block_num).get_data())
            return_block.get_machine_state().set_storage(
                self.processing_block.get_machine_state().get_storage().duplicate(new_block_num))
            return_block.get_machine_state().set_balance(
                deepcopy(self.processing_block.get_machine_state().get_balance())
            )
            return_block.block_state |= self.processing_block.block_state
            # print('balance prev')
            # print(self.processing_block.get_machine_state().get_balance())
            # print('balance next')
            # print(return_block.get_machine_state().get_balance())


            self.processing_block = return_block

            return return_block


    def add_basic_block(self, basic_block: BasicBlock):
        self.basic_blocks.append(basic_block)

    def add_visited_block(self, basic_block: BasicBlock):
        self.__visited_blocks.append(basic_block)

    def get_basic_blocks(self):
        return self.basic_blocks

    def get_visited_blocks(self):
        return self.__visited_blocks

    def add_edge(self, origin: BasicBlock, dest: BasicBlock):
        dest.depth = origin.depth + 1
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
            if len(d.get_mnemonic_as_str())==0:
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

            nodedefine += '"'
            if ' CALL\l' == mnemonics[n][-7:] or ' CREATE\l' == mnemonics[n][-9:]:
                nodedefine += ',color = red'
            elif (' STOP\l' in mnemonics[n]
                  or ' RETURN\l' in mnemonics[n]
                  or ' REVERT\l' in mnemonics[n]) and 'block' + str(n) + ' ->' in edges:
                nodedefine += ',color = green'
            nodedefine += '];\n'

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

