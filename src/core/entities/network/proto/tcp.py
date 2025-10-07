from src.core.entities.network.packets.data import RawData
from src.core.entities.network.proto.proto import TransportLayerProtocol
from src.core.entities.network.packets.tcp_packet import TCPPacket
from src.core.entities.network.stats.l4_stats import L4Stats


class TransmissionControlProtocol(TransportLayerProtocol):

    def __init__(self, router, message: RawData, mtu=0):
        super().__init__(router, message)
        self.mtu = mtu
        self.data_left = 0
        self.l4_stats = L4Stats()
        if self.message is not None:
            self.data_left = self.message.msg_size
            if self.mtu == 0:
                self.mtu = self.message.msg_size + TCPPacket.HEADER_SIZE

    def transmit_segment(self, packet: TCPPacket):
        self.l4_stats.update_tx_stats(packet)
        self.router.transmit(packet)
        # Actually this is a hack and violates the "realistic network model" design:
        # in real networks there is way to measure jitter only if packet
        # is received on RX side and the response frame with timestamp has been
        # delivered to the sender.
        # But implementing this would make single-threaded and non-interruptible design overcomplicated.
        # Our use case is actually measuring time for all packets,
        # including dropped ones (especially for the variable error rate test suit)
        self.l4_stats.inc_time(packet.time_travelled)

    def receive_message(self):
        packet = self.router.pop_transport_layer_packet()
        self.l4_stats.update_rx_stats(packet)
        return packet

    def transmit_message(self, dest_router_id):
        if self.data_left <= 0:
            return

        if self.data_left > self.mtu:
            segment_size = self.mtu - TCPPacket.HEADER_SIZE
        else:
            segment_size = self.data_left

        packet = TCPPacket(self.router.id, dest_router_id, segment_size, TCPPacket.DATA)
        self.transmit_segment(packet)
        pass

    def confirm_delivery(self):
        self.data_left -= self.mtu - TCPPacket.HEADER_SIZE


    def mgmt(self, dest_router_id, mgmt_type):
        self.transmit_segment(TCPPacket(self.router.id, dest_router_id, 0, mgmt_type))

    def syn(self, dest_router_id):
        self.mgmt(dest_router_id, TCPPacket.SYN)

    def ack(self, dest_router_id):
        self.mgmt(dest_router_id, TCPPacket.ACK)

    def syn_ack(self, dest_router_id):
        self.mgmt(dest_router_id, TCPPacket.SYN_ACK)

    def fin(self, dest_router_id):
        self.mgmt(dest_router_id, TCPPacket.FIN)
