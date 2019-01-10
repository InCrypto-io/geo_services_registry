from pymongo import MongoClient
import time
from threading import Thread


class EventCache:
    def __init__(self, connection, gsr, db_url, confirmation_count):
        self.connection = connection
        self.gsr = gsr
        self.confirmation_count = confirmation_count
        self.client = MongoClient(db_url)
        self.db = self.client['events']
        self.events_collection = self.db["events"]
        self.stop_collect_events = True

    def collect(self):
        self.stop_collect_events = False
        worker = Thread(target=self.process_events, daemon=True)
        worker.start()

    def process_events(self):
        event_filter = self.gsr.contract.eventFilter("Vote", {'fromBlock': 3660400, 'toBlock': 3660500})
        print("created filter id", event_filter.filter_id)
        event_logs = event_filter.get_all_entries()
        print("event_logs", event_logs)

        self.connection.get_web3().eth.uninstallFilter(event_filter.filter_id)

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
