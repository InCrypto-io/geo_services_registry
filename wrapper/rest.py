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


class REST:
    def __init__(self):
        self.eth_connection = EthConnection(config.WEB3_PROVIDER, config.MNEMONIC)

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

    async def handle(self, request):
        text = "/" + request.match_info.get('request') + "\n" + str(request.rel_url.query)
        return web.Response(text=text)

    async def get_current_block_number(self, request):
        pass

    async def erase(self, request):
        pass

    async def get_registries(self, request):
        pass

    async def is_registry_exist(self, request):
        pass

    async def get_votes_list(self, request):
        pass

    async def get_vote_for_candidate(self, request):
        pass

    def process_events(self):
        while self.allow_process_events:
            self.registries_cache.update()
            self.registries_cache.update_current_block()
            time.sleep(1)

    def launch(self):
        app = web.Application()
        app.add_routes([web.get('/', self.handle),
                        web.get('/blocks/currentBlock', self.get_current_block_number),
                        web.get('/blocks/erase', self.erase),
                        web.get('/registries/list', self.get_registries),
                        web.get('/registries/exist', self.is_registry_exist),
                        web.get('/votes/list', self.is_registry_exist),
                        web.get('/votes/candidate', self.get_vote_for_candidate),
                        web.get('/{request}', self.handle)])

        self.allow_process_events = True
        self.event_cache.collect()

        worker = Thread(target=self.process_events, daemon=True)
        worker.start()

        web.run_app(app)

        self.allow_process_events = False
        self.event_cache.stop_collect()

        while worker.is_alive():
            time.sleep(1)
