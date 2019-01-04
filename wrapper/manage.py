#!/usr/bin/python
import config
from geo_service_registry import GeoServiceRegistry

if __name__ == "__main__":
    print("+++++++++++Manage++++++++++++")
    print("WEB3_PROVIDER", config.WEB3_PROVIDER)
    print("GEOSERVICEREGISTRY_ADDRESS", config.GEOSERVICEREGISTRY_ADDRESS)
    print("GEOTOKEN_ADDRESS", config.GEOTOKEN_ADDRESS)

    gsr = GeoServiceRegistry(config.WEB3_PROVIDER, config.GEOSERVICEREGISTRY_ADDRESS)
    gsr.test()

    print("+++++++++Done!+++++++++++++++++++")
