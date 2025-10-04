from src.core.entities.network.packets.packet import TransportLayerPacket
from src.core.entities.network.stats.stats import StatsTable


class L4Stats(object):
    def __init__(self):
        self.stats = StatsTable()
        self.time = 0
        self.retransmits = 0

    def update_tx_stats(self, packet: TransportLayerPacket):
        if packet is not None:
            self.stats.update_tx_stats(packet.get_message_size() - packet.get_header_size(), packet.get_header_size())
        pass

    def update_rx_stats(self, packet: TransportLayerPacket):
        if packet is not None:
            self.stats.update_rx_stats(packet.get_message_size() - packet.get_header_size(), packet.get_header_size())
            self.time += packet.time_travelled
        pass