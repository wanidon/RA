import pytest
from data_structures import Bytecode
from exceptions import EVMbytecodeError


class TestBytecode:

    def test_init(self):
        Bytecode("0123456789abcdef")

        with pytest.raises(EVMbytecodeError):
            Bytecode("0123456789abcdef0")
        
        with pytest.raises(EVMbytecodeError):
            Bytecode("0g")
        
    def test_append(self):
        bytecode = Bytecode()
        bytecode.append("0b")
        
        with pytest.raises(EVMbytecodeError):
            bytecode.append("0g")

        with pytest.raises(EVMbytecodeError):
            bytecode.append("0")

    def test_slice(self):
        bytecode = Bytecode("0123456789abcdef")
        assert bytecode[0] == "01"
        assert bytecode[7] == "ef"
        assert bytecode[1:7] == ["23", "45", "67", "89", "ab", "cd"]
