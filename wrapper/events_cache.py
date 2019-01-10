from pymongo import MongoClient
import time
from threading import Thread


class EventCache:
    def __init__(self, connection, gsr_address, db_url, confirmation_count):
        self.connection = connection
        self.gsr_address = gsr_address
        self.confirmation_count = confirmation_count
        self.client = MongoClient(db_url)
        self.db = self.client['events' + str(gsr_address)]
        self.events_collection = self.db["events"]
        self.stop_collect_events = True

    def collect(self):
        self.stop_collect_events = False
        worker = Thread(target=self.process_events, daemon=True)
        worker.start()

    def process_events(self):
        event_filter = self.connection.get_web3().eth.filter({
            "address": self.gsr_address,
        })
        print("created filter id", event_filter.filter_id)
        while not self.stop_collect_events:
            print("check events")
            for event in event_filter.get_new_entries():
                self.write_event(event)
            time.sleep(5)

    def stop_collect(self):
        self.stop_collect_events = True

    def write_event(self, event):
        print("write event", event)
        # self.events_collection.insert_one(event)

    def erase_all(self, from_block_number=0):
        pass

    def get_events_count(self):
        pass

    def get_event(self, index):
        pass

    def get_events_in_range(self, block_start, block_end):
        pass
