from src.core.entities.network.packets.packet import TransportLayerPacket


class UDPPacket(TransportLayerPacket):
    HEADER_SIZE = 8
    def __init__(self, src, dst, message_size):
        TransportLayerPacket.__init__(self, src, dst, message_size)

    def get_header_size(self):
        return self.HEADER_SIZE