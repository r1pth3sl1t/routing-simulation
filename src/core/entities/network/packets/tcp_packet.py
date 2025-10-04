from src.core.entities.network.packets.packet import TransportLayerPacket


class TCPPacket(TransportLayerPacket):
    DATA = 0
    ACK = 1
    SYN_ACK = 2
    SYN = 3
    FIN = 4
    HEADER_SIZE = 20

    def __init__(self, source_router_id, dest_router_id, message_size, packet_type):
        TransportLayerPacket.__init__(self, source_router_id, dest_router_id, message_size)
        self.type = packet_type
        pass

    def get_header_size(self):
        return self.HEADER_SIZE
