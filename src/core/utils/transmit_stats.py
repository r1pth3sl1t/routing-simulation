class TransmitStats:
    def __init__(self, tx_l3_stats, tx_l4_stats, rx_l3_stats, rx_l4_stats, message_size):
        self.tx_l3_stats = tx_l3_stats
        self.tx_l4_stats = tx_l4_stats
        self.rx_l3_stats = rx_l3_stats
        self.rx_l4_stats = rx_l4_stats
        self.message_size = message_size
        pass

    def get_error_rate(self):
        err = 1.0 - (self.rx_l3_stats.stats.rx_stats.overall_bytes / self.message_size)
        if err < 0.0:
            err = 0
        return err

    def get_overall_time(self):
        return self.rx_l4_stats.time + self.tx_l4_stats.time

    def get_retransmits(self):
        return self.tx_l4_stats.retransmits + self.rx_l4_stats.retransmits
