import json
import web3
from web3 import Web3

import os


class GeoServiceRegistry:

    def __init__(self, provider, address):
        interface_file = open("./build/contracts/GeoServiceRegistry.json", "r")
        contract_interface = json.load(interface_file)
        interface_file.close()

        print("provider", provider)

        if("http" in provider.lower()):
            w3 = Web3(Web3.HTTPProvider(provider))
        else:
            w3 = Web3(Web3.WebsocketProvider(provider))
        print("w3.isConnected()", w3.isConnected())

        w3.eth.defaultAccount = w3.eth.accounts[0]
        print("w3.eth.defaultAccount", w3.eth.defaultAccount)

        self.contract = w3.eth.contract(
            address=address,
            abi=contract_interface['abi'],
        )

    def is_registry_exist(self, registry_name):
        return self.contract.functions.isRegistryExist(registry_name).call()

    def test(self):
        reg_name = "provider"
        print("isRegistryExist {} - {}".format(reg_name, self.is_registry_exist(reg_name)))
        reg_name = "gggggggggg"
        print("isRegistryExist {} - {}".format(reg_name, self.is_registry_exist(reg_name)))
