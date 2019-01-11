import time
import pymongo
from pymongo import MongoClient


class RegistriesCache:
    def __init__(self, event_cache, gsr_created_at_block, db_url):
        self.event_cache = event_cache
        self.gsr_created_at_block = gsr_created_at_block

        self.client = MongoClient(db_url)
        self.db = self.client['geo']
        self.collection_name_prefix = "registry_"
        self.__remove_uncompleted_blocks()

    def update(self, wait_for_block_number=0):

        if wait_for_block_number > 0:
            while wait_for_block_number >= self.event_cache.last_processed_block:
                time.sleep(10)

        count_blocks = (self.event_cache.last_processed_block - self.gsr_created_at_block)
        last_processed_block = self.get_last_processed_block()
        while last_processed_block < count_blocks:
            self.prepare(self.gsr_created_at_block + last_processed_block + 1000)
            last_processed_block = last_processed_block + 1000

    def prepare(self, block_number):
        pass

    def erase(self, block_number=0):
        '''
        :param block_number: if 0 erase all
        '''
        pass

    def is_registry_exist(self, registry_name, block_number):
        pass

    def get_total_votes_for_candidate(self, candidate_address, registry_name, block_number):
        pass

    def get_winners_list(self, registry_name, block_number):
        pass

    def get_last_processed_block(self):
        result = 0
        for e in self.db.collection_names():
            if self.collection_name_prefix in e:
                number = int(e[len(self.collection_name_prefix)::])
                if result < number:
                    result = number
        return result

    def __remove_uncompleted_blocks(self):
        pass
