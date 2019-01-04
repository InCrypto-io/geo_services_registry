import json
from web3 import Web3


class GeoServiceRegistry:

    def __init__(self, connection, address):
        interface_file = open("./build/contracts/GeoServiceRegistry.json", "r")
        contract_interface = json.load(interface_file)
        interface_file.close()

        w3 = connection.get_web3()

        self.contract = w3.eth.contract(
            address=address,
            abi=contract_interface['abi'],
        )

    def is_registry_exist(self, registry_name):
        return self.contract.functions.isRegistryExist(registry_name).call()

    def withdraw(amount):
        pass

    def vote_service_lockup_for_new_registry(registry_name):
        pass

    def vote_service_lockup(registry_name, _candidates, _amounts):
        pass

    def vote_service_for_new_registry(registry_name):
        pass

    def vote_service(registry_name, _candidates, _amounts):
        pass

    def sum_of_array(array):
        pass

    def set_vote_weight_in_lockup_period(new_amount):
        pass

    def make_deposit(addition_amount):
        pass
