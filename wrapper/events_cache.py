

class EventCache:
    def __init__(self, connection, gsr_address):
        self.connection = connection
        self.gsr_address = gsr_address

    def collect(self):
        pass

    def stop_collect(self):
        pass

    def erase_all(self, from_block_number=0):
        pass

    def get_events_count(self):
        pass

    def get_event(self, index):
        pass

    def get_events_in_range(self, block_start, block_end):
        pass
