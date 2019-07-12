# Data structures associated with Ethereum

## Storage
## Memory
## Stack
## Returndata
Unlimited byte array similar to  memory. When the size of return value is fixed, it looks like the stack is being used as a place to store the return value.

## Account
generated for each contract, differently from original Ethereum, it (will) only holds immutable variables
- code,EVM bytecode, immutable
- codesize,len(code), immutable
- balance, mutable?
- the list of CFG node, e.g. [node1,node2,,]
- the edges of CFG, e.g.{origin_node:[dest1,dest2]}
- account_num
- cfg_filename

## System_state
denoted σ, generated once, ~~the mapping between account_address -> Account~~
- list of Accounts
- block_hashes, the mapping between block_number -> hash

## Execution_state ~~Machine_state~~
denoted µ, generated for *each CFG node*. differently from original Ethereum, this includes Storage for convinience to analysis
- pc
- Memory
- Stack
- Storage
- Returndata
- Calldata  
this will be used to send data
- ~~gas_available~~
- ~~i (memsize?)~~

## Execution_environment
denoted I, generated for each execution
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



# Data structures for convenience of the analysis
## Node
Each CFG node holds its own Execution_state at the end of its symbolic execution.
- Execution_state ~~Machine_state~~
- Code with the number of lines (bytes) contained in this node
- List of conditional expressions to reach this node
- ~~origin~~
- ~~destination~~
- node_number
## edges
- node_number -> [dest1,dest2,,,]

