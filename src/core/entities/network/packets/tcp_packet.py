from src.core.entities.network.packets.packet import TransportLayerPacket


class TCPPacket(TransportLayerPacket):
    DATA = 0
    ACK = 1
    SYN = 2
    FIN = 3
    HEADER_SIZE = 20

    def __init__(self, source_router_id, dest_router_id, message_size, type):
        TransportLayerPacket.__init__(self, source_router_id, dest_router_id, message_size)
        self.type = type
        self.ack_number = 0
        pass

    def get_header_size(self):
        return self.HEADER_SIZE
