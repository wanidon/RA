#coding:utf-8
from data_structures import WorldState
if __name__ == 'main':
    # 主たるコントラクトのコードを標準入力から受け取る
    code_primaly = '0123456789'
    primalies = [code_primaly]
    # 従たるコントラクトのコード
    code_secoundaly = 'abcdef'
    secoundalies = [code_secoundaly]


    #system_state作成
    system_state = WorldState()
    while primalies:
        p = code_primaly.pop()



