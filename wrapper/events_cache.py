from pymongo import MongoClient

class EventCache:
    def __init__(self, connection, gsr_address, db_url, confirmation_count):
        self.connection = connection
        self.gsr_address = gsr_address
        self.confirmation_count = confirmation_count
        self.client = MongoClient(db_url)
        self.db = self.client['events' + str(gsr_address)]
        self.events_collection = self.db["events"]

    def collect(self):
        pass

    def stop_collect(self):
        pass

    def write_event(self, event):
        self.events_collection.insert_one(event)

    def erase_all(self, from_block_number=0):
        pass

    def get_events_count(self):
        pass

    def get_event(self, index):
        pass

    def get_events_in_range(self, block_start, block_end):
        pass
