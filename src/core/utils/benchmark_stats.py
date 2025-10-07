class BenchmarkStats:
    def __init__(self):
        self.transmit_stats = []

    def add_record(self, transmit_stats):
        self.transmit_stats.append(transmit_stats)
        pass
