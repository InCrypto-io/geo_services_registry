import json


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

        if len(connection.get_accounts()) > 0:
            self.account = connection.get_accounts()[0]
        else:
            self.account = ""

    def set_account(self, account):
        self.account = account

    def is_registry_exist(self, registry_name):
        return self.contract.functions.isRegistryExist(registry_name).call()

    def withdraw(self, amount):
        return self.contract.functions.withdraw(amount) \
            .transact({'from': self.account, 'gas': 100000})

    def vote_service_for_new_registry(self, registry_name):
        return self.contract.functions.voteServiceForNewRegistry(registry_name) \
            .transact({'from': self.account, 'gas': 100000})

    def vote_service_lockup_for_new_registry(self, registry_name):
        return self.contract.functions.voteServiceLockupForNewRegistry(registry_name) \
            .transact({'from': self.account, 'gas': 100000})

    def vote_service(self, registry_name, _candidates, _amounts):
        return self.contract.functions.voteService(registry_name, _candidates, _amounts) \
            .transact({'from': self.account, 'gas': 100000})

    def vote_service_lockup(self, registry_name, _candidates, _amounts):
        return self.contract.functions.voteServiceLockup(registry_name, _candidates, _amounts) \
            .transact({'from': self.account, 'gas': 100000})

    def set_vote_weight_in_lockup_period(self, new_amount):
        return self.contract.functions.setVoteWeightInLockupPeriod(new_amount) \
            .transact({'from': self.account, 'gas': 100000})

    def make_deposit(self, addition_amount):
        return self.contract.functions.makeDeposit(addition_amount) \
            .transact({'from': self.account, 'gas': 100000})
