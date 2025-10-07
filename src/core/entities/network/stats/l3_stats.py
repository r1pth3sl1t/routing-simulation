from src.core.entities.network.packets.ip_packet import IPLayerPacket
from src.core.entities.network.stats.stats import StatsTable


class L3Stats():
    def __init__(self):
        self.stats = StatsTable()

    def update_rx_stats(self, packet: IPLayerPacket):
        self.stats.update_rx_stats(packet.frag_size - IPLayerPacket.HEADER_SIZE, IPLayerPacket.HEADER_SIZE)
        pass

    def update_tx_stats(self, packet: IPLayerPacket):
        self.stats.update_tx_stats(packet.frag_size - IPLayerPacket.HEADER_SIZE, IPLayerPacket.HEADER_SIZE)
        pass
