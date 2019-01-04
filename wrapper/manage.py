#!/usr/bin/python
import config
from geo_service_registry import GeoServiceRegistry
from eth_connection import EthConnection

if __name__ == "__main__":
    print("+++++++++++Manage++++++++++++")
    print("WEB3_PROVIDER", config.WEB3_PROVIDER)
    print("GEOSERVICEREGISTRY_ADDRESS", config.GEOSERVICEREGISTRY_ADDRESS)
    print("GEOTOKEN_ADDRESS", config.GEOTOKEN_ADDRESS)

    eth_connection = EthConnection(config.WEB3_PROVIDER)

    gsr = GeoServiceRegistry(eth_connection, config.GEOSERVICEREGISTRY_ADDRESS)
    gsr.test()

    print("+++++++++Done!+++++++++++++++++++")
