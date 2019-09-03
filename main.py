#coding:utf-8
from data_structures import WorldState
from vm import VM

if __name__ == '__main__':

    world_state = WorldState()

    # 主たるコントラクトのコードを標準入力から受け取る
    code_primaly = '6001600201' # + 1 2
    primaly_contracts = [world_state.add_account(code_primaly)]

    print(primaly_contracts)

    # # 従たるコントラクトのコード
    # secondaly_contracts = []
    # with open(0,'r') as f:
    #     for line in f.readlines():
    #         secondaly_contracts.append(world_state.add_account(line.rstrip()))

    vm = VM(world_state)
    for addr in primaly_contracts:
        vm.init_state(addr)




