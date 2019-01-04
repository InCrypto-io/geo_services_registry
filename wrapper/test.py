import config
from geo_service_registry import GeoServiceRegistry
from eth_connection import EthConnection


class Test:
    def __init__(self):
        self.eth_connection = EthConnection(config.WEB3_PROVIDER)
        self.gsr = GeoServiceRegistry(self.eth_connection, config.GEOSERVICEREGISTRY_ADDRESS)

    def test(self):
        self.test_gsr()

    def test_gsr(self):
        print("Test gsr isRegistryExist")
        reg_name = "provider"
        print("isRegistryExist {} - {}".format(reg_name, self.gsr.is_registry_exist(reg_name)))
        reg_name = "not_exist_registry"
        print("isRegistryExist {} - {}".format(reg_name, self.gsr.is_registry_exist(reg_name)))
