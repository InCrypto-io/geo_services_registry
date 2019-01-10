import pymongo
from pymongo import MongoClient
import time
from threading import Thread


class EventCache:
    def __init__(self, connection, gsr, gsr_created_at_block, db_url, confirmation_count):
        self.connection = connection
        self.gsr = gsr
        self.confirmation_count = confirmation_count
        self.client = MongoClient(db_url)
        self.db = self.client['events_1']
        self.events_collection = self.db["events_collection"]
        self.check_and_wait_connection_to_db()
        self.events_collection.create_index([
            ("blockNumber", pymongo.ASCENDING),
            ("logIndex", pymongo.ASCENDING)
        ], unique=True)
        self.stop_collect_events = True

        self.last_processed_block = gsr_created_at_block
        if self.get_events_count():
            try:
                self.last_processed_block = int(self.get_event(self.get_events_count() - 1)["blockNumber"])
            except:
                print("Can't determinate last processed block")

    def collect(self):
        self.stop_collect_events = False
        worker = Thread(target=self.process_events, daemon=True)
        worker.start()

    def process_events(self):
        new_block_filter = self.connection.get_web3().eth.filter('latest')
        while not self.stop_collect_events:
            for _ in new_block_filter.get_new_entries():
                last_block_number = self.connection.get_web3().eth.blockNumber
                print("exist new block", last_block_number)
                while self.last_processed_block + self.confirmation_count <= last_block_number:
                    print("try get event for block:", self.last_processed_block + 1)
                    for event_name in self.gsr.get_events_list():
                        event_filter = self.gsr.contract.eventFilter(event_name,
                                                                     {'fromBlock': self.last_processed_block + 1,
                                                                      'toBlock': self.last_processed_block + 1})
                        for event in event_filter.get_all_entries():
                            self.write_event(event)
                        self.connection.get_web3().eth.uninstallFilter(event_filter.filter_id)
                    self.last_processed_block = self.last_processed_block + 1
            time.sleep(10)

        self.connection.get_web3().eth.uninstallFilter(new_block_filter.filter_id)

    def stop_collect(self):
        self.stop_collect_events = True

    def write_event(self, event):
        print("write event", event)
        for f in ["event", "logIndex", "transactionIndex", "transactionHash", "address", "blockHash", "blockNumber"]:
            if f not in event:
                print("Event not contains expected fields")
                break
        data = {
            'event': event['event'],
            'logIndex': event['logIndex'],
            'transactionIndex': event['transactionIndex'],
            'transactionHash': event['transactionHash'],
            'address': event['address'],
            'blockHash': event['blockHash'],
            'blockNumber': event['blockNumber']
        }
        self.events_collection.insert_one(data)

    def erase_all(self, from_block_number=0):
        pass

    def get_events_count(self):
        return self.events_collection.count()

    def get_event(self, index):
        return self.events_collection.find().sort(["blockNumber", "logIndex"]).skip(index).limit(1)

    def get_events_in_range(self, block_start, block_end):
        pass

    def check_and_wait_connection_to_db(self):
        while True:
            try:
                print("Check connection to mongodb server")
                print(self.client.server_info())
                break
            except pymongo.errors.ServerSelectionTimeoutError:
                print("Can't connect to mongodb server")
