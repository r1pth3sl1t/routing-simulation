class Stats:
    def __init__(self):
        self.data_bytes = 0
        self.mgmt_bytes = 0
        self.overall_bytes = 0

    def update(self, data_bytes, mgmt_bytes):
        self.data_bytes += data_bytes
        self.mgmt_bytes += mgmt_bytes
        self.overall_bytes += data_bytes + mgmt_bytes
        pass

class StatsTable(Stats):
    def __init__(self):
        self.tx_stats = Stats()
        self.rx_stats = Stats()

    def update_rx_stats(self, data_bytes, mgmt_bytes):
        self.rx_stats.update(data_bytes, mgmt_bytes)
        pass

    def update_tx_stats(self, data_bytes, mgmt_bytes):
        self.tx_stats.update(data_bytes, mgmt_bytes)
        pass
