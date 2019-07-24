# 分岐におけるBasicBlockの扱い

## プログラム開始時
1. 新しいBasicBlockを作成
    - 同時に空のmachine_stateも作られる
1. 新しいexecution_environmentを作成してブロックにセット
1. 新しいBasicBlockを実行

## 分岐しないとき & 分岐ある場合に続行する(ジャンプしない)とき
1. 現在のBasicBlockをCFGmanagerに保存
1. 現在のBasicBlockを複製
1. machine_stateに新しいpcの値をセット
1. 新しいBasicBlockを実行

## 分岐するとき(ジャンプするとき)
### ジャンプ先となるブロックの作成とプッシュ
深さ優先探索のため、あとでロールバックして実行する
1. 現在のBasicBlockを複製
1. machine_stateにジャンプ先のpcの値をセット
1. dfs_stackに作成したBasicBlockをpush

### 分岐へのロールバック時
1. 現在のBasicBlockをCFGmanagerに保存
1. dfs_stackからpopしたBasicBlockを実行

# createの初期化コード実行時やcallにおいて外部ジャンプする際のBasicBlockの扱い
## 外部ジャンプするとき
### 戻り先となるブロックの作成とプッシュ
1. 現在のBasicBlockをCFGmanagerに保存
1. 現在のBasicBlockを複製
1. machine_stateに戻り先となるpc(=現在の次の命令)をセット
1. call_stackに作成したBasicBlockをpush
### 外部コードのブロックの作成
1. 新しいブロックを作成
1. 新しいexecutioin_environmentを作成して新しいブロックにセット
1. 現在のmachine_stateのmemory, stack(, returndata)をdeepcopyして新しいブロックにセット
1. 新しいブロックを実行

## 外部から戻るとき
1. 現在のBasicBlockをCFGmanagerに保存
1. call_stackからpopしたブロックに現在のmachine_stateのstack, memory(, returndata)をdeepcopyしてセット
1. ブロックを実行


# delegatecallにおいて外部ジャンプする際のBasicBlockの扱い
## 外部ジャンプするとき
### 戻り先となるブロックの作成とプッシュ
1. 現在のBasicBlockをCFGmanagerに保存
1. 現在のBasicBlockを複製
1. machine_stateに戻り先となるpc(=現在の次の命令)をセット
1. call_stackに作成したBasicBlockをpush
### 外部コードのブロックの作成
1. 新しいブロックを作成
1. 新しいexecutioin_environmentを作成して新しいブロックにセット
1. 現在のmachine_stateのstorage, memory, stack(, returndata)をdeepcopyして新しいブロックにセット
1. 新しいブロックを実行

## 外部から戻るとき
1. 現在のBasicBlockをCFGmanagerに保存
1. call_stackからpopしたブロックに現在のmachine_stateのstorage, stack, memory(, returndata)をdeepcopyしてセット
1. ブロックを実行

# BasicBlockの複製について
mnemonisは空  
machine_stateはmutableなのでdeepcopy  
execution_environmentはimmutableなので参照を代入するだけ(shallowcopyでもない)
