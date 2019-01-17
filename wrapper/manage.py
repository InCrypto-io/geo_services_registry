#!/usr/bin/python
import config
from test import Test
from rest import REST

if __name__ == "__main__":
    print("+++++++++++Manage++++++++++++")
    print("WEB3_PROVIDER", config.WEB3_PROVIDER)
    print("GEOSERVICEREGISTRY_ADDRESS", config.GEOSERVICEREGISTRY_ADDRESS)
    print("GEOTOKEN_ADDRESS", config.GEOTOKEN_ADDRESS)
    print("COMMAND_ARGS", config.COMMAND_ARGS)

    if "TEST" in config.COMMAND_ARGS:
        test = Test()
        # test.test()
        # test.test_events_cache()
        test.test_registries_cache()

    if "REST" in config.COMMAND_ARGS:
        rest = REST()
        rest.launch()

    print("+++++++++Done!+++++++++++++++++++")
