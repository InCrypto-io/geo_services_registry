from web3 import Web3


class EthConnection:
    def __init__(self, provider):
        print("selected provider is {}".format(provider))

        assert len(provider) > 0

        if "http" in provider.lower():
            self.w3 = Web3(Web3.HTTPProvider(provider))
        else:
            self.w3 = Web3(Web3.WebsocketProvider(provider))

        print("connected to {}: {}".format(provider, self.w3.isConnected()))

        if len(self.w3.eth.accounts) > 0:
            self.w3.eth.defaultAccount = self.w3.eth.accounts[0]

    def get_web3(self):
        return self.w3

    def get_accounts(self):
        return self.w3.eth.accounts
