import config
from eth_connection import EthConnection
from geo_service_registry import GeoServiceRegistry
from geo_token import GEOToken
from events_cache import EventCache
import time


class Test:
    def __init__(self):
        self.eth_connection = EthConnection(config.WEB3_PROVIDER, config.MNEMONIC)
        self.gsr = GeoServiceRegistry(self.eth_connection, config.GEOSERVICEREGISTRY_ADDRESS)
        self.geo = GEOToken(self.eth_connection, config.GEOTOKEN_ADDRESS)

    def test(self):
        self.test_gsr()

    def test_gsr(self):
        print("Test gsr isRegistryExist")
        reg_name = "provider"
        print("isRegistryExist {} - {}".format(reg_name, self.gsr.is_registry_exist(reg_name)))
        reg_name = "not_exist_registry"
        print("isRegistryExist {} - {}".format(reg_name, self.gsr.is_registry_exist(reg_name)))

        accounts = self.eth_connection.get_accounts()

        owner = accounts[0]
        user1 = accounts[1]
        user2 = accounts[2]

        print("Transfer token to users")
        self.geo.set_sender(owner)
        self.geo.transfer(user1, 123123)
        self.geo.transfer(user2, 123123)

        print("Balance of {}: {} tokens".format(user1, self.geo.balance_of(user1)))

        print("Request for set vote size")
        self.gsr.set_sender(user1)
        self.gsr.set_vote_weight_in_lockup_period(10000)

        print("Create registry")
        reg_name = "created_registry_"
        counter = 0
        while True:
            if not self.gsr.is_registry_exist(reg_name + str(counter)):
                break
            counter = counter + 1
        reg_name = reg_name + str(counter)
        print("isRegistryExist {} - {}".format(reg_name, self.gsr.is_registry_exist(reg_name)))
        print("Add registry")
        self.gsr.vote_service_lockup_for_new_registry(reg_name)
        print("isRegistryExist {} - {}".format(reg_name, self.gsr.is_registry_exist(reg_name)))

        print("Try catch revert:")
        try:
            self.gsr.vote_service_lockup_for_new_registry("provider")
        except:
            print("\tOk!!!")
        else:
            print("\tExpected revert. Fail!!!")

        print("Try vote for candidate")
        tx_hash = self.gsr.vote_service_lockup(reg_name, [owner, user1], [5000, 5000])
        print("\tresult transaction hash {}".format(tx_hash.hex()))

        print("Try get events:")
        tx_receipt = self.eth_connection.get_web3().eth.waitForTransactionReceipt(tx_hash)

        events_list = self.gsr.contract.events.Vote().processReceipt(tx_receipt)
        print("\tlogs", events_list)

        # event_filter = self.gsr.contract.events.Vote.createFilter(fromBlock=0)
        # while True:
        #     for event in event_filter.get_new_entries():
        #         print(event)
        #     time.sleep(5)

    def test_events_cache(self):
        print("Test event cache")
        event_cache = EventCache(self.eth_connection, config.GEOSERVICEREGISTRY_ADDRESS, config.DB_URL, config.CONFIRMATION_COUNT)
        event_cache.collect()

        accounts = self.eth_connection.get_accounts()
        owner = accounts[0]
        user1 = accounts[1]
        for _ in range(20):
            print("push new event, vote_service_lockup")
            self.gsr.set_sender(user1)
            tx = self.gsr.vote_service_lockup("provider", [owner, user1], [5000, 5000])
            print("tx", str(tx))
            time.sleep(10)
