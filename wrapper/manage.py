#!/usr/bin/python
import config
from test import Test

if __name__ == "__main__":
    print("+++++++++++Manage++++++++++++")
    print("WEB3_PROVIDER", config.WEB3_PROVIDER)
    print("GEOSERVICEREGISTRY_ADDRESS", config.GEOSERVICEREGISTRY_ADDRESS)
    print("GEOTOKEN_ADDRESS", config.GEOTOKEN_ADDRESS)

    test = Test()
    test.test()

    print("+++++++++Done!+++++++++++++++++++")
