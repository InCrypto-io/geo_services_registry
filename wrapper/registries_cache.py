import time
import pymongo
from pymongo import MongoClient


class RegistriesCache:
    def __init__(self, event_cache, gsr_created_at_block, db_url, interval_for_preprocessed_blocks):
        self.event_cache = event_cache
        self.gsr_created_at_block = gsr_created_at_block

        self.collection_name_prefix = "registry_"
        self.temp_collection_name_prefix = "reg_temp_"
        self.interval_for_preprocessed_blocks = interval_for_preprocessed_blocks

        self.client = MongoClient(db_url)
        self.db = self.client['db_geo_registries']

        self.__remove_uncompleted_blocks()

        # self.db.command("copyTo", [self.db["bbbbbb"], self.db["a"]])

    def update(self, wait_for_block_number=0):
        if wait_for_block_number > 0:
            while wait_for_block_number >= self.event_cache.last_processed_block:
                time.sleep(10)

        last_processed_block = self.get_last_processed_block()
        if last_processed_block < self.gsr_created_at_block:
            last_processed_block = self.gsr_created_at_block
        while last_processed_block < self.event_cache.last_processed_block:
            self.prepare(last_processed_block + self.interval_for_preprocessed_blocks)
            last_processed_block = last_processed_block + self.interval_for_preprocessed_blocks

        # todo for current

    def prepare(self, block_number):
        print("prepare", block_number)
        assert block_number > self.get_last_processed_block()
        assert (block_number - self.gsr_created_at_block) % self.interval_for_preprocessed_blocks == 0

        previous_block = (((block_number - self.gsr_created_at_block) // self.interval_for_preprocessed_blocks)
                          * self.interval_for_preprocessed_blocks) - self.interval_for_preprocessed_blocks

        # reg name -> voter -> candidate -> amount in percent
        votes = {}
        # voter -> amount
        weights = {}
        # names
        registries = []

        if previous_block < 0:
            previous_block = 0
        if previous_block > 1:
            previous_votes = self.db[self.collection_name_prefix + "votes_" + str(block_number)]
            previous_weights = self.db[self.collection_name_prefix + "weights_" + str(block_number)]
            previous_registries = self.db[self.collection_name_prefix + "registries_" + str(block_number)]

        # events = self.event_cache.get_events_in_range(previous_block, block_number)
        events = self.event_cache.get_events_in_range(self.gsr_created_at_block, block_number)

        print("events", events.count())

        for event in events:
            if event["event"] == "Deposit":
                weights[event["_voter"]] = event["_fullSize"]
            elif event["event"] == "Withdrawal":
                weights[event["_voter"]] = weights[event["_voter"]] - event["_amountWithdraw"]
                assert weights[event["_voter"]] >= 0
                if weights[event["_voter"]] == 0:
                    for reg_name in registries:
                        if event["_voter"] in votes[reg_name]:
                            del votes[reg_name][event["_voter"]]
            elif event["event"] == "Vote":
                votes[event["_name"]][event["_voter"]] = {}
                votes[event["_name"]][event["_voter"]][event["_candidate"]] = event["_candidate"]
            elif event["event"] == "NewRegistry":
                registries.append(event["_name"])
                votes[event["_name"]] = {}

        # reg name -> candidate -> total tokens
        participants = {}

        for reg_name in registries:
            participants[reg_name] = {}
            for voter in votes[reg_name].keys():
                for candidate in votes[reg_name][voter].keys():
                    if candidate not in participants[reg_name].keys():
                        participants[reg_name][candidate] = 0
                    else:
                        participants[reg_name][candidate] = participants[reg_name][candidate] \
                                                            + (votes[reg_name][voter][candidate] * weights[voter])

        # reg name -> sorted array -> [candidate, total tokens]
        winners = []
        for reg_name in registries:
            winners[reg_name] = []
            for candidate in participants[reg_name].keys():
                winners[reg_name].append([candidate, participants[reg_name][candidate]])
            winners[reg_name].sort(key=lambda candidate_and_total: candidate_and_total[1])

        print(winners)

        # collection.rename(self.collection_name_prefix + str(block_number))

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
