from web3 import Web3
from libs.ethBIP44.ethLib import HDPrivateKey, HDKey


class EthConnection:
    def __init__(self, provider, mnemonic):
        print("selected provider is {}".format(provider))

        assert len(provider) > 0

        if "http" in provider.lower():
            self.w3 = Web3(Web3.HTTPProvider(provider))
        else:
            self.w3 = Web3(Web3.WebsocketProvider(provider))

        print("connected to {}: {}".format(provider, self.w3.isConnected()))

        if len(self.w3.eth.accounts) > 0:
            self.w3.eth.defaultAccount = self.w3.eth.accounts[0]

        try:
            self.accounts = []
            self.priv_keys = []

            master_key = HDPrivateKey.master_key_from_mnemonic(mnemonic)
            root_keys = HDKey.from_path(master_key, "m/44'/60'/0'")
            acct_priv_key = root_keys[-1]
            der_path="m/44'/60'/0'/"
            for i in range(0,10):
                keys = HDKey.from_path(acct_priv_key, der_path + str(i))
                priv_key = keys[-1]
                print("keys", keys)
                print("priv_key", priv_key)
                pub_key = priv_key.public_key
                address = pub_key.address()
                self.accounts.append(self.w3.toChecksumAddress(address))
        except Exception:
            self.accounts = []



    def get_web3(self):
        return self.w3

    def get_accounts(self):
        if len(self.w3.eth.accounts) == 0:
            return self.w3.eth.accounts
        return self.accounts
