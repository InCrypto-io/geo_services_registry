from aiohttp import web
import config
from eth_connection import EthConnection
from geo_service_registry import GeoServiceRegistry
from geo_token import GEOToken
from events_cache import EventCache
import time
from registries_cache import RegistriesCache
from settings import Settings
from threading import Thread
import json


class REST:
    def __init__(self):
        self.eth_connection = EthConnection(config.WEB3_PROVIDER, config.MNEMONIC, config.DB_URL)

        self.gsr = GeoServiceRegistry(self.eth_connection, config.GEOSERVICEREGISTRY_ADDRESS)
        self.geo = GEOToken(self.eth_connection, config.GEOTOKEN_ADDRESS)

        settings = Settings(config.DB_URL)

        self.event_cache = EventCache(
            self.eth_connection,
            self.gsr,
            config.GEOSERVICEREGISTRY_CREATED_AT_BLOCK,
            config.DB_URL,
            config.CONFIRMATION_COUNT,
            settings)

        self.registries_cache = RegistriesCache(self.event_cache, config.GEOSERVICEREGISTRY_CREATED_AT_BLOCK,
                                                config.DB_URL,
                                                config.INTERVAL_FOR_PREPROCESSED_BLOCKS, settings,
                                                config.VOTES_ROUND_TO_NUMBER_OF_DIGIT)

        self.allow_process_events = False

    def get_first_block_number(self, request):
        text = str(config.GEOSERVICEREGISTRY_CREATED_AT_BLOCK)
        return web.Response(text=text)

    def get_current_block_number(self, request):
        text = str(self.registries_cache.get_current_preprocessed_block_number())
        return web.Response(text=text)

    def get_registries(self, request):
        if "blockNumber" not in request.rel_url.query.keys():
            return web.Response(status=400)
        try:
            block_number = int(request.rel_url.query["blockNumber"])
            if block_number < config.GEOSERVICEREGISTRY_CREATED_AT_BLOCK \
                    or block_number > self.registries_cache.get_current_preprocessed_block_number():
                return web.Response(status=404)
            text = json.dumps({
                "registries": self.registries_cache.get_registry_list(block_number),
                "blockNumber": block_number
            })
            return web.Response(text=text)
        except ValueError:
            return web.Response(status=400)

    def is_registry_exist(self, request):
        if "registryName" not in request.rel_url.query.keys():
            return web.Response(status=400)
        if "blockNumber" not in request.rel_url.query.keys():
            return web.Response(status=400)
        try:
            registry_name = str(request.rel_url.query["registryName"])
            block_number = int(request.rel_url.query["blockNumber"])
            if block_number < config.GEOSERVICEREGISTRY_CREATED_AT_BLOCK \
                    or block_number > self.registries_cache.get_current_preprocessed_block_number():
                return web.Response(status=404)
            text = json.dumps({
                "registry": registry_name,
                "exist": self.registries_cache.is_registry_exist(registry_name, block_number),
                "blockNumber": block_number
            })
            return web.Response(text=text)
        except ValueError:
            return web.Response(status=400)

    def get_winners_list(self, request):
        if "registryName" not in request.rel_url.query.keys():
            return web.Response(status=400)
        if "blockNumber" not in request.rel_url.query.keys():
            return web.Response(status=400)
        try:
            registry_name = str(request.rel_url.query["registryName"])
            block_number = int(request.rel_url.query["blockNumber"])
            if block_number < config.GEOSERVICEREGISTRY_CREATED_AT_BLOCK \
                    or block_number > self.registries_cache.get_current_preprocessed_block_number():
                return web.Response(status=404)
            text = json.dumps({
                "registry": registry_name,
                "winners": self.registries_cache.get_winners_list(registry_name, block_number),
                "blockNumber": block_number
            })
            return web.Response(text=text)
        except ValueError:
            return web.Response(status=400)

    def get_vote_for_candidate(self, request):
        if "address" not in request.rel_url.query.keys():
            return web.Response(status=400)
        if "registryName" not in request.rel_url.query.keys():
            return web.Response(status=400)
        if "blockNumber" not in request.rel_url.query.keys():
            return web.Response(status=400)
        try:
            address = str(request.rel_url.query["address"])
            registry_name = str(request.rel_url.query["registryName"])
            block_number = int(request.rel_url.query["blockNumber"])
            if block_number < config.GEOSERVICEREGISTRY_CREATED_AT_BLOCK \
                    or block_number > self.registries_cache.get_current_preprocessed_block_number():
                return web.Response(status=404)
            text = json.dumps({
                "registry": registry_name,
                "address": address,
                "tokens": self.registries_cache.get_total_votes_for_candidate(address, registry_name, block_number),
                "blockNumber": block_number
            })
            return web.Response(text=text)
        except ValueError:
            return web.Response(status=400)

    def get_gas_price(self, request):
        text = str(self.eth_connection.get_gas_price())
        return web.Response(text=text)

    def get_ethereum_accounts(self, request):
        text = json.dumps({
            "addresses": self.eth_connection.get_accounts()
        })
        return web.Response(text=text)

    def process_events(self):
        while self.allow_process_events:
            self.registries_cache.update()
            self.registries_cache.update_current_block()
            time.sleep(1)

    def launch(self):
        app = web.Application()
        app.add_routes([web.get('/blocks/firstBlock', self.get_first_block_number),
                        web.get('/blocks/currentBlock', self.get_current_block_number),
                        web.get('/registries/list', self.get_registries),
                        web.get('/registries/exist', self.is_registry_exist),
                        web.get('/votes/list', self.get_winners_list),
                        web.get('/votes/candidate', self.get_vote_for_candidate),
                        web.get('/eth/gasPrice', self.get_gas_price),
                        web.get('/eth/accounts', self.get_ethereum_accounts),
                        ])

        self.allow_process_events = True
        self.event_cache.collect()

        worker = Thread(target=self.process_events, daemon=True)
        worker.start()

        web.run_app(app)

        self.allow_process_events = False
        self.event_cache.stop_collect()

        while worker.is_alive():
            time.sleep(1)
