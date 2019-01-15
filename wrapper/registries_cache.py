import pymongo
from pymongo import MongoClient


class RegistriesCache:
    def __init__(self, event_cache, gsr_created_at_block, db_url, interval_for_preprocessed_blocks, settings):
        self.event_cache = event_cache
        self.gsr_created_at_block = gsr_created_at_block
        self.settings = settings

        self.collection_name_prefix = "registry_"
        self.interval_for_preprocessed_blocks = interval_for_preprocessed_blocks

        self.client = MongoClient(db_url)
        self.db = self.client['db_geo_registries']

    def update(self):
        last_processed_block_number = self.__get_last_preprocessed_block_number()
        if self.event_cache.get_last_processed_block_number() < self.gsr_created_at_block:
            return
        while last_processed_block_number + self.interval_for_preprocessed_blocks \
                < self.event_cache.get_last_processed_block_number():
            self.prepare(last_processed_block_number + self.interval_for_preprocessed_blocks)
            last_processed_block_number = last_processed_block_number + self.interval_for_preprocessed_blocks
            self.__set_last_preprocessed_block_number(last_processed_block_number)

        current_preprocessed_block_number = self.__get_current_preprocessed_block_number()
        if current_preprocessed_block_number >= self.gsr_created_at_block:
            return
        if current_preprocessed_block_number < self.event_cache.get_last_processed_block_number():
            if current_preprocessed_block_number != self.__determine_previous_preprocessed_block(
                    self.event_cache.get_last_processed_block_number()):
                self.__remove_dbs_for_block_number(current_preprocessed_block_number)
            if self.event_cache.get_last_processed_block_number() != self.__get_last_preprocessed_block_number():
                self.prepare(self.event_cache.get_last_processed_block_number())
            self.__set_current_preprocessed_block_number(self.event_cache.get_last_processed_block_number())

    def prepare(self, block_number):
        print("prepare", block_number)
        assert block_number > self.__get_last_preprocessed_block_number()
        assert block_number >= self.gsr_created_at_block

        previous_block = self.__determine_previous_preprocessed_block(block_number)

        # reg name -> voter -> candidate -> amount in percent
        votes = {}
        # voter -> amount
        weights = {}
        # names
        registries = []
        # reg name -> sorted array -> [candidate, total tokens]
        winners = {}

        if previous_block > self.gsr_created_at_block:
            self.__load_from_db(votes, weights, registries, winners, previous_block)

        winners = {}
        self.__apply_events(votes, weights, registries, winners, previous_block, block_number)

        self.__save_to_db(votes, weights, registries, winners, block_number)

    def __load_from_db(self, votes, weights, registries, winners, block_number):
        assert len(votes) == 0
        assert len(weights) == 0
        assert len(registries) == 0
        assert len(winners) == 0
        collection_votes = self.db[self.collection_name_prefix + "votes_" + str(block_number)]
        collection_weights = self.db[self.collection_name_prefix + "weights_" + str(block_number)]
        collection_registries = self.db[self.collection_name_prefix + "registries_" + str(block_number)]
        collection_winners = self.db[self.collection_name_prefix + "winners_" + str(block_number)]

        for document in collection_registries.find():
            registries.append(document["name"])
            votes[document["name"]] = {}
            winners[document["name"]] = []

        for document in collection_votes.find():
            if document["voter"] not in votes[document["registry_name"]].keys():
                votes[document["registry_name"]][document["voter"]] = {}
            votes[document["registry_name"]][document["voter"]][document["candidate"]] = document["percentage_amount"]

        for document in collection_weights.find():
            weights[document["voter"]] = document["amount"]

        for document in collection_winners.find().sort([("position", pymongo.ASCENDING)]):
            winners[document["registry_name"]].append([document["candidate"], document["amount"]])

    def __save_to_db(self, votes, weights, registries, winners, block_number):
        collection_votes = self.db[self.collection_name_prefix + "votes_" + str(block_number)]
        collection_weights = self.db[self.collection_name_prefix + "weights_" + str(block_number)]
        collection_registries = self.db[self.collection_name_prefix + "registries_" + str(block_number)]
        collection_winners = self.db[self.collection_name_prefix + "winners_" + str(block_number)]

        if collection_votes.find({}).count():
            collection_votes.remove({})
        if collection_weights.find({}).count():
            collection_weights.remove({})
        if collection_registries.find({}).count():
            collection_registries.remove({})
        if collection_winners.find({}).count():
            collection_winners.remove({})

        for reg_name in votes.keys():
            for voter in votes[reg_name].keys():
                for candidate in votes[reg_name][voter].keys():
                    collection_votes.insert_one({
                        "registry_name": reg_name,
                        "voter": voter,
                        "candidate": candidate,
                        "percentage_amount": votes[reg_name][voter][candidate]
                    })

        for voter in weights.keys():
            collection_weights.insert_one({
                "voter": voter,
                "amount": weights[voter]
            })

        for reg_name in registries:
            collection_registries.insert_one({
                "name": reg_name
            })

        for reg_name in winners.keys():
            for i in range(0, len(winners[reg_name])):
                collection_winners.insert_one({
                    "registry_name": reg_name,
                    "candidate": winners[reg_name][i][0],
                    "amount": winners[reg_name][i][1],
                    "position": i
                })

    def __remove_dbs_for_block_number(self, block_number):
        self.client.drop_database(self.collection_name_prefix + "votes_" + str(block_number))
        self.client.drop_database(self.collection_name_prefix + "weights_" + str(block_number))
        self.client.drop_database(self.collection_name_prefix + "registries_" + str(block_number))
        self.client.drop_database(self.collection_name_prefix + "winners_" + str(block_number))

    def __apply_events(self, votes, weights, registries, winners, from_block_number, to_block_number):
        assert len(winners) == 0
        events = self.event_cache.get_events_in_range(from_block_number, to_block_number)

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
                if event["_voter"] not in votes[event["_name"]].keys():
                    votes[event["_name"]][event["_voter"]] = {}
                votes[event["_name"]][event["_voter"]][event["_candidate"]] = event["_amount"]
            elif event["event"] == "NewRegistry":
                if event["_name"] not in registries:
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
                    weight_in_tokens = (votes[reg_name][voter][candidate] * weights[voter] / 10000)
                    participants[reg_name][candidate] = participants[reg_name][candidate] + weight_in_tokens

        for reg_name in registries:
            winners[reg_name] = []
            for candidate in participants[reg_name].keys():
                winners[reg_name].append([candidate, participants[reg_name][candidate]])
            winners[reg_name].sort(key=lambda candidate_and_total: candidate_and_total[1])

        for reg_name in winners.keys():
            for i in range(0, len(winners[reg_name])):
                if winners[reg_name][i][1] == 0:
                    del winners[reg_name][i]

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

    def __determine_previous_preprocessed_block(self, block_number):
        previous_block = self.gsr_created_at_block
        if block_number >= self.gsr_created_at_block + self.interval_for_preprocessed_blocks + 1:
            previous_block = (((block_number - self.gsr_created_at_block) // self.interval_for_preprocessed_blocks - 1)
                              * self.interval_for_preprocessed_blocks) \
                             + self.gsr_created_at_block
        return previous_block

    def __get_last_preprocessed_block_number(self):
        result = self.settings.get_value("last_preprocessed_block_number")
        if not result:
            result = self.gsr_created_at_block
        return result

    def __set_last_preprocessed_block_number(self, value):
        self.settings.set_value("last_preprocessed_block_number", value)

    def __get_current_preprocessed_block_number(self):
        result = self.settings.get_value("current_preprocessed_block_number")
        if not result:
            result = 0
        return result

    def __set_current_preprocessed_block_number(self, value):
        self.settings.set_value("current_preprocessed_block_number", value)
