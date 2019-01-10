from pymongo import MongoClient
import time
from threading import Thread


class EventCache:
    def __init__(self, connection, gsr_address, db_url, confirmation_count, gsr):
        self.connection = connection
        self.gsr_address = gsr_address
        self.confirmation_count = confirmation_count
        self.client = MongoClient(db_url)
        self.db = self.client['events' + str(gsr_address)]
        self.events_collection = self.db["events"]
        self.stop_collect_events = True

        self.gsr = gsr

    def collect(self):
        self.stop_collect_events = False
        worker = Thread(target=self.process_events, daemon=True)
        worker.start()

    def process_events(self):
        event_filter = self.connection.get_web3().eth.filter({
            "fromBlock": 0,
            'toBlock': 1000100000000,
            "address": self.gsr_address,
        })

        # event_filter = self.gsr.contract.events.Vote.createFilter(fromBlock=0)
        # event_filter = self.connection.get_web3().eth.getFilterLogs(event_filter.filter_id)

        filter_ = self.connection.get_web3().eth.filter({})

        # logs = self.connection.get_web3().eth.getFilterLogs(filter_.filter_id)
        # for log in logs:
        #     print("log", log)

        print("created filter id", event_filter.filter_id)

        event_filterdfghdfgd = self.gsr.contract.eventFilter("Vote", {'fromBlock': 3660400, 'toBlock': 3660500})
        print("created filter id", event_filterdfghdfgd.filter_id)
        event_logs = event_filterdfghdfgd.get_all_entries()
        print("event_logs", event_logs)

        while not self.stop_collect_events:
            print("check events")
            for event in event_filter.get_new_entries():
                self.write_event(event)
            time.sleep(5)

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
