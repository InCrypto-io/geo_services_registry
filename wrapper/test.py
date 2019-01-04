import config
from eth_connection import EthConnection
from geo_service_registry import GeoServiceRegistry
from geo_token import GEOToken


class Test:
    def __init__(self):
        self.eth_connection = EthConnection(config.WEB3_PROVIDER)
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
        self.geo.set_account(owner)
        self.geo.transfer(user1, 123123)
        self.geo.transfer(user2, 123123)

        print("Request for set vote size")
        self.gsr.set_account(user1)
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
