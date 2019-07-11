# Data structures associated with Ethereum

## system_state
account_address -> Account
## Account
- code,EVM bytecode
- codesize,len(code)
- Storage
- balance
- [node1,node2,,]
- edges
- cfg_filename
## Machine_state
- ~~gas_available~~
- pc
- Memory
- ~~i (memsize?)~~
- Stack
## Storage
## Memory
## Stack
## Returndata
## Execution_environment
- Ia, the address of the account which owns the code that is executing. == *address(this)*
- ~~Io,the sender address of the transaction that originated this execution.~~
- Ip, the price of gas in the transaction that origi- nated this execution. == *tx.gasprice*
- Id,the byte array that is the input data to this execution; if the execution agent is a transaction, this would be the transaction data. == *msg.data* ==*Call Data*
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
## block_hashes
block_number -> hash


# Data structures for convenience of the analysis
## Node
Each CFG node holds its own Machine_state at the end of its symbolic execution.
- Machine_state
- code contained the node
- ~~origin~~
- ~~destination~~
- node_number
## edges
- node_number -> [dest1,dest2,,,]

