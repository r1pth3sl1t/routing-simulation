from src.core import network
from src.core.entities.network.packets.packet import TransportLayerPacket


class IPLayerPacket:
    HEADER_SIZE = 20
    sequence_number = 0 # Global serial id of seq_num to simplify simulation and guarantee uniqueness

    def __init__(self, router_id, dest, packet: TransportLayerPacket, sequence_number, frag_num, more_fragments):
        self.router_id = router_id
        self.dest = dest
        self.transport_layer_packet = packet
        if packet is not None:
            self.msg_size = packet.get_message_size() + self.HEADER_SIZE
        else:
            self.msg_size = self.HEADER_SIZE

        self.seq_num = self.sequence_number
        self.frag_num = frag_num
        self.more_fragments = more_fragments
        self.frag_size = self.msg_size
        if self.msg_size > network.MTU:
            if self.more_fragments:
                self.frag_size = network.MTU
            else:
                # For the simulation purposes we do not need to pass real data inside the packets, and
                # management traffic size can be computed, so optimize ip header creation
                # by not computing packet size outsize of packet creation and passing it in constructor but inside it
                # last fragment size = rest of message from L4 + size of all IP headers in previous fragments
                self.frag_size = self.msg_size % network.MTU + (self.msg_size // network.MTU) * IPLayerPacket.HEADER_SIZE

    @staticmethod
    def next_sequence_number(ip_layer_packet=None):
        IPLayerPacket.sequence_number = IPLayerPacket.sequence_number + 1
        return IPLayerPacket.sequence_number
