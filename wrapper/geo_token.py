import json


class GEOToken:

    def __init__(self, connection, address):
        interface_file = open("./build/contracts/GEOToken.json", "r")
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

    def transfer_from(self, sender, receiver, value):
        return self.contract.functions.transferFrom(sender, receiver, value) \
            .transact({'from': self.account, 'gas': 100000})

    def transfer(self, receiver, value):
        return self.contract.functions.transfer(receiver, value) \
            .transact({'from': self.account, 'gas': 100000})

    def total_supply(self):
        return self.contract.functions.totalSupply().call()

    def set_individual_lockup_expire_time(self, who, time):
        return self.contract.functions.setIndividualLockupExpireTime(who, time) \
            .transact({'from': self.account, 'gas': 100000})

    def deny_transfer_in_lockup_period(self, who):
        return self.contract.functions.denyTransferInLockupPeriod(who) \
            .transact({'from': self.account, 'gas': 100000})

    def allow_transfer_in_lockup_period(self, who):
        return self.contract.functions.allowTransferInLockupPeriod(who) \
            .transact({'from': self.account, 'gas': 100000})

    def is_lockup_expired(self, _who):
        return self.contract.functions.isLockupExpired(_who).call()

    def increase_allowance(self, spender, added_value):
        return self.contract.functions.spender(spender, added_value) \
            .transact({'from': self.account, 'gas': 100000})

    def decrease_allowance(self, spender, subtracted_value):
        return self.contract.functions.spender(spender, subtracted_value) \
            .transact({'from': self.account, 'gas': 100000})

    def burn(self, account, value):
        return self.contract.functions.burn(account, value) \
            .transact({'from': self.account, 'gas': 100000})

    def mint(self, account, value):
        return self.contract.functions.mint(account, value) \
            .transact({'from': self.account, 'gas': 100000})

    def balance_of(self, owner):
        return self.contract.functions.balanceOf(owner).call()

    def approve(self, spender, value):
        return self.contract.functions.approve(spender, value) \
            .transact({'from': self.account, 'gas': 100000})

    def allowance(self, owner, spender):
        return self.contract.functions.allowance(owner, spender) \
            .transact({'from': self.account, 'gas': 100000})
