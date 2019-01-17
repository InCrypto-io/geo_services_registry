from web3 import Web3
from libs.ethBIP44.ethLib import HDPrivateKey, HDKey
from pymongo import MongoClient


class EthConnection:
    def __init__(self, provider, mnemonic, db_url):
        print("selected provider is {}".format(provider))

        assert len(provider) > 0

        self.client = MongoClient(db_url)
        self.db = self.client['db_geo_transactions']
        self.transactions_collection = self.db["transactions"]

        self.w3 = Web3(Web3.WebsocketProvider(provider))

        print("connected to {}: {}".format(provider, self.w3.isConnected()))

        if len(mnemonic):
            try:
                self.accounts = []
                self.private_keys = []
                master_key = HDPrivateKey.master_key_from_mnemonic(mnemonic)
                root_keys = HDKey.from_path(master_key, "m/44'/60'/0'/0")
                acct_priv_key = root_keys[-1]
                for i in range(0, 10):
                    keys = HDKey.from_path(acct_priv_key, str(i))
                    priv_key = keys[-1]
                    pub_key = priv_key.public_key
                    address = pub_key.address()
                    self.accounts.append(self.w3.toChecksumAddress(address))
                    self.private_keys.append("0x" + priv_key._key.to_hex())
            except Exception:
                self.accounts = []

        self.nonces = {}

    def get_web3(self):
        return self.w3

    def get_accounts(self):
        if len(self.accounts):
            return self.accounts
        return self.w3.eth.accounts

    def get_nonce(self, address):
        if address in self.nonces.keys():
            self.nonces[address] = self.nonces[address] + 1
            return self.nonces[address]
        self.nonces[address] = self.w3.eth.getTransactionCount(address, "pending")
        return self.nonces[address]

    def sign_and_send_transaction(self, address, raw_transaction):
        assert address in self.get_accounts()
        private_key = self.private_keys[self.get_accounts().index(address)]
        signed_transaction = self.w3.eth.account.signTransaction(raw_transaction, private_key)
        tx_hash = self.w3.eth.sendRawTransaction(signed_transaction.rawTransaction)
        self.__store_raw_transaction(address, raw_transaction, tx_hash)
        return tx_hash

    def get_gas_price(self):
        return int(self.w3.eth.gasPrice)

    def __store_raw_transaction(self, address, raw_transaction, tx_hash):
        self.transactions_collection.insert_one({
            "from": address,
            "raw_transaction": raw_transaction,
            "hash": tx_hash
        })

    def __get_stored_raw_transaction(self, tx_hash):
        return self.transactions_collection.find_one({
            "hash": tx_hash
        })

    def erase(self):
        self.transactions_collection.remove({})

    def resend(self, tx_hash, new_gas_price=0):
        previous = self.__get_stored_raw_transaction(tx_hash)
        if new_gas_price == 0:
            new_gas_price = self.get_gas_price()
        previous["raw_transaction"]["gasPrice"] = new_gas_price
        return self.sign_and_send_transaction(previous["from"],
                                              previous["raw_transaction"])
