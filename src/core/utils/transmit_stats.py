class TransmitStats:
    def __init__(self, tx_l3_stats, tx_l4_stats, rx_l3_stats, rx_l4_stats, message_size, mtu, proto, err_rate):
        self.tx_l3_stats = tx_l3_stats
        self.tx_l4_stats = tx_l4_stats
        self.rx_l3_stats = rx_l3_stats
        self.rx_l4_stats = rx_l4_stats
        self.message_size = message_size
        self.mtu = mtu
        self.proto = proto
        self.err_rate = err_rate
        pass

    def get_error_rate(self):
        err = 1.0 - (self.rx_l4_stats.stats.rx_stats.data_bytes / self.message_size)
        if err < 0.0:
            err = 0
        return err * 100

    def get_overall_time(self):
        return self.rx_l4_stats.time + self.tx_l4_stats.time

    def get_retransmits(self):
        return self.tx_l4_stats.retransmits + self.rx_l4_stats.retransmits

    def get_mgmt_bytes_ratio(self):
        return (self.tx_l4_stats.stats.tx_stats.mgmt_bytes +
                self.tx_l3_stats.stats.tx_stats.mgmt_bytes +
                self.rx_l4_stats.stats.tx_stats.mgmt_bytes +
                self.tx_l3_stats.stats.tx_stats.mgmt_bytes) / self.tx_l3_stats.stats.tx_stats.overall_bytes

    def get_data_bytes_ratio(self):
        return self.tx_l4_stats.stats.tx_stats.data_bytes / self.tx_l4_stats.stats.tx_stats.overall_bytes