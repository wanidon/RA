from vm import VM
from data_structures import WorldState

# get contract code
bytecode = '45600557fe44600a57fe4300'
primary_contracts = [bytecode]
secondary_contract = None
tertiary_contracts = []

world_state = WorldState()
vm = VM(world_state)
for b in primary_contracts:
    vm.add_primary_contract(b)
vm.run_all()