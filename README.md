# RA
Re-entrancy Analyzer, driven by symbolic execution.   
This tool simulates function calling which may cause re-enctancy attack, and detect it. This can also verify construction of new contract as external calling.
## Requirement
- `cmake` command (used for building z3 solver)
    - for Mac: `brew install cmake`
- Python3 (3.7 or higher is confirmed to run)
- Python modules
    - z3-solver (this installation may take about 10 minutes)
    - pysha3 (used for convenience to represent sha3 output)
- Graphviz (optional; used to draw the execution path)

## Usage
1. Run ra.py.  
    `python3 ra.py`
1. Get some EVM bytecode to be verified. If you want to verify your Solidity code, you can get its bytecode as follows:
  `solc -o {OUTPUT_DIR} --bin-runtime {YOUT_SOLIDITY_FILE} `
1. Give the bytecode to standard input. For example, the following code has a simple re-entrancy.
    `606060405260043610610041576000357c0100000000000000000000000000000000000000000000000000000000900463ffffffff1680633ccfd60b14610046575b600080fd5b341561005157600080fd5b61005961005b565b005b3373ffffffffffffffffffffffffffffffffffffffff166000803373ffffffffffffffffffffffffffffffffffffffff1673ffffffffffffffffffffffffffffffffffffffff1681526020019081526020016000205460405180602001905060006040518083038185875af192505050156101155760008060003373ffffffffffffffffffffffffffffffffffffffff1673ffffffffffffffffffffffffffffffffffffffff168152602001908152602001600020819055505b5600a165627a7a72305820e598d1a576b5047521cba20260ee9579fee29311bfbb5623191a49ca74a1e4380029`
1. If the given code has re-entrancy, RA teach you the combination of functions which may cause re-entrancy as tuple of function IDs.  
    `('0x3ccfd60b', '0x3ccfd60b', True, 6.267011556017678)`  
    In this case, The first `'0x3ccfd60b'` is function ID of the first called function, and the second `'0x3ccfd60b'` is function ID of the second called (called by malicious contract) function.
## Limitation
- ~~RA cannnot create new contract whose code will be determine dynamically(such part will be symbol variable). It is due to the data type which represents contract. Ra just uses a string as EVM bytecode. Thus, if it is replaced with python list, or temporally fixes such dynamic code, you can analyse such contracts.~~  
 Now you can verify code constructing new contract.
- Some EVM opcodes are not implemented in RA's VM.

## License
This program is released under the MIT license.