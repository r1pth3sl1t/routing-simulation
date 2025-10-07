from src.core.entities.network.packets.data import RawData
from src.core.entities.network.packets.udp_packet import UDPPacket
from src.core.entities.network.proto.proto import TransportLayerProtocol
from src.core.entities.network.stats.l4_stats import L4Stats


class UserDatagramProtocol(TransportLayerProtocol):

    def __init__(self, router, message: RawData, mtu=0):
        super(UserDatagramProtocol, self).__init__(router, message)
        self.l4_stats = L4Stats()
        self.mtu = mtu
        self.data_left = 0
        if message is not None:
            self.data_left = self.message.msg_size
            if mtu == 0:
                self.mtu = self.message.msg_size + UDPPacket.HEADER_SIZE

    def transmit_message(self, dest_router_id):
        while self.data_left > 0:
            if self.data_left > self.mtu:
                packet_size = self.mtu - UDPPacket.HEADER_SIZE
            else:
                packet_size = self.data_left

            datagram = UDPPacket(self.router.id, dest_router_id, packet_size)
            self.l4_stats.update_tx_stats(datagram)
            self.data_left -= packet_size
            self.router.transmit(datagram)
            # Actually this is a hack and violates the "realistic network model" design:
            # in real networks there is way to measure jitter only if packet
            # is received on RX side and the response frame with timestamp has been
            # delivered to the sender.
            # But implementing this would make single-threaded and non-interruptible design overcomplicated.
            # Our use case is actually measuring time for all packets,
            # including dropped ones (especially for the variable error rate test suit)
            self.l4_stats.inc_time(datagram.time_travelled)

    def receive_message(self):
        while True:
            datagram = self.router.pop_transport_layer_packet()
            if datagram is None:
                break

            self.l4_stats.update_rx_stats(datagram)
