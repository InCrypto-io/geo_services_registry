import time
import pymongo
from pymongo import MongoClient


class RegistriesCache:
    def __init__(self, event_cache, gsr_created_at_block, db_url):
        self.event_cache = event_cache
        self.gsr_created_at_block = gsr_created_at_block

        self.collection_name_prefix = "registry_"
        self.temp_collection_name_prefix = "reg_temp_"
        self.interval_for_preprocessed_blocks = 1000

        self.client = MongoClient(db_url)
        self.db = self.client['geo']

        self.__remove_uncompleted_blocks()

    def update(self, wait_for_block_number=0):

        if wait_for_block_number > 0:
            while wait_for_block_number >= self.event_cache.last_processed_block:
                time.sleep(10)

        count_blocks = (self.event_cache.last_processed_block - self.gsr_created_at_block)
        last_processed_block = self.get_last_processed_block()
        if last_processed_block < self.interval_for_preprocessed_blocks:
            last_processed_block = self.interval_for_preprocessed_blocks
        while last_processed_block < count_blocks:
            self.prepare(self.gsr_created_at_block + last_processed_block + self.interval_for_preprocessed_blocks)
            last_processed_block = last_processed_block + self.interval_for_preprocessed_blocks

    def prepare(self, block_number):
        assert block_number < self.get_last_processed_block()
        collection = self.db[self.temp_collection_name_prefix + str(block_number)]

        collection.rename(self.collection_name_prefix + str(block_number))

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
        for element in self.db.collection_names():
            if self.collection_name_prefix in element:
                number = int(element[len(self.collection_name_prefix)::])
                if result < number:
                    result = number
        return result

    def __remove_uncompleted_blocks(self):
        for element in self.db.collection_names():
            if self.temp_collection_name_prefix in element:
                self.db[element].drop()
