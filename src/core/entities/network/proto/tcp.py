from src.core.entities.network.packets.data import RawData
from src.core.entities.network.proto.proto import TransportLayerProtocol
from src.core.entities.network.packets.tcp_packet import TCPPacket


class TransmissionControlProtocol(TransportLayerProtocol):

    def __init__(self, router, message: RawData, mtu=0):
        super().__init__(router, message)
        self.mtu = mtu
        self.data_left = 0
        if self.message is not None:
            self.data_left = self.message.msg_size
            if self.mtu == 0:
                self.mtu = self.message.msg_size
        print("data left %s" % self.data_left)

    def transmit_segment(self, packet: TCPPacket):
        self.router.transmit(packet)

    def receive_segment(self):
        return self.router.pop_transport_layer_packet()

    def transmit_message(self, dest_router_id):
        if self.data_left <= 0:
            return

        segment_size = self.message.msg_size
        if self.mtu:
            if self.data_left > self.mtu:
                segment_size = self.mtu - TCPPacket.HEADER_SIZE
            else:
                segment_size = self.data_left

        packet = TCPPacket(self.router.id, dest_router_id, segment_size, TCPPacket.DATA)
        self.transmit_segment(packet)
        pass

    def confirm_delivery(self):
        self.data_left -= self.mtu -TCPPacket.HEADER_SIZE


    def mgmt(self, dest_router_id, mgmt_type):
        self.transmit_segment(TCPPacket(self.router.id, dest_router_id, 0, mgmt_type))

    def syn(self, dest_router_id):
        self.mgmt(dest_router_id, TCPPacket.SYN)

    def ack(self, dest_router_id):
        self.mgmt(dest_router_id, TCPPacket.ACK)

    def fin(self, dest_router_id):
        self.mgmt(dest_router_id, TCPPacket.FIN)
