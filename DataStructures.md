
## parts
### Storage
### Memory
### Stack
### Returndata
Unlimited byte array similar to  memory. When the size of return value is fixed, it looks like the stack is being used as a place to store the return value.
### Calldata
### Basic_block
##### フィールド
Each CFG node holds its own Execution_state at the end of its symbolic execution.
- account_number
- block_number

- machine_state
- execution_state
- mnemonics,  with the number of lines (bytes) contained in this node, list of (bytes,mnemonic)
- path_condition ~~List of conditional expressions (path conditions) to reach this node~~
- jump_condition  
condition for JUMPI
- (dest_to_continue)
- (dest_to_jump)
- ~~origin~~
- ~~destination~~
- call_stack
- dfs_stack
- CFG_name
##### メソッド
- duplicate
## execution of this tool
### System_state
denoted σ, generated once, ~~the mapping between account_address -> Account~~
- ~~list of execution_environment~~
- block_hashes  
the mapping between block_number -> hash
- accounts
the mapping between address and Account
- bytecode_que
this stores contract bytecode to be called(given contract) or executed(created contract)

### Account
generated for each contract
- account_num
- code,EVM bytecode  
immutable
- codesize,len(code)  
immutable
- balance  
mutable?
- storage




## execution of contract
### VM
##### フィールド
- system_state (given as a parameter of the constructor)
- CFG_manager

- memory = CFGmanager.processingblock.machine_state.memory
- stack = CFGmanager.processingblock.machine_state.stack
- storage = CFGmanager.processingblock.machine_state.storage
- pc = CFGmanager.processingblock.machine_state.pc
- code = CFGmanager.processingblock.machine_state.execution_environment.code
- execution_environment = CFGmanager.processingblock.machine_state.execution_environment



##### 機能
- expand_block
    

### Machine_state
denoted µ, generated for each execution and a snapshot of this is stored in each CFG block.  
For convinience of analysis, containing Stack
- pc
- Memory
- Stack
- ~~Returndata~~
- ~~gas_available~~
- ~~i (memsize?)~~

### CFG_manager
##### データ
- edges  
indexed by block number, and contains the list of destinations [[dest_of_block_0_0,dest_of_block_0_1,,,].[dest_of_block_1_0,,,]]
- list of blocks
- num_block = len(list of blocks)  
新しいブロックを生成する際に割り振る番号として利用

- processing_block
- call_stack

##### 機能
- 

## contract
### Execution_environment
denoted I, generated for each contract  
- eenum, number of execution environment
- Ia, the address of the account which owns the code that is executing. == *address(this)*
- ~~Io,the sender address of the transaction that originated this execution.~~
- Ip, the price of gas in the transaction that origi- nated this execution. == *tx.gasprice*
- Id,the byte array that is the input data to this execution; if the execution agent is a transaction, this would be the transaction data. == *msg.data* ==*Call Data*  
this will be used to receive data
- Is, the address of the account which caused the code to be executing; if the execution agent is a transaction, this would be the transaction sender. == *msg.caller*
- Iv, the value, in Wei, passed to this account as part of the same procedure as execution; if the execution agent is a transaction, this would be the transaction value. == *msg.value*
- Ib, the byte array that is the machine code to be executed. == *sytem_state[address(this)].code*
- IH, the block header of the present block.
    - *block.coinbase*
    - *block.timestamp*
    - *block.number*
    - *block.difficulty*
    - *block.gaslimit*
- ~~Ie, the depth of the present message-call or contract-creation (i.e. the number of CALLs or CREATEs being executed at present).~~
- ~~Iw, the permission to make modifications to the state.~~





