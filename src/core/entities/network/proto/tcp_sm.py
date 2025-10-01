from src.core.entities.network.packets.tcp_packet import TCPPacket


class TCPStateMachine:
    IDLE = 0
    CONNECT = 1
    THREE_WAY_HANDSHAKE_SYN_ACK = 4
    THREE_WAY_HANDSHAKE_ACK_WAIT = 5
    THREE_WAY_HANDSHAKE_ACK = 6
    TRANSMIT = 7
    RETRANSMIT = 8
    ACKNOWLEDGE = 9
    ACKNOWLEDGE_WAIT = 10
    DONE = 11

    def __init__(self, tcp_proto, connection_retries=3):
        self.state = self.IDLE
        self.tcp_proto = tcp_proto
        self.connection_established = False
        self.destination_router_id = -1
        self.connection_retries = connection_retries
        self.transmission_done = False
        self.states = {
            TCPStateMachine.IDLE: self.idle,
            TCPStateMachine.THREE_WAY_HANDSHAKE_ACK: self.three_way_handshake_ack,
            TCPStateMachine.THREE_WAY_HANDSHAKE_SYN_ACK: self.three_way_handshake_syn_ack,
            TCPStateMachine.TRANSMIT: self.transmit_segment,
            TCPStateMachine.CONNECT: self.connect,
            TCPStateMachine.RETRANSMIT: self.retransmit_segment,
            TCPStateMachine.ACKNOWLEDGE: self.ack

        }

    def set_dest_router_id(self, dst):
        self.destination_router_id = dst

    def init_connect(self):
        if self.destination_router_id:
            self.state = TCPStateMachine.CONNECT

    def init_transmit(self):
        if self.destination_router_id and self.connection_established:
            self.state = TCPStateMachine.TRANSMIT

    # Listen to all incoming messages
    def idle(self):
        if self.connection_established:
            self.receive_segment()
        else:
            self.three_way_handshake_syn_listen()
        pass

    def next(self):
        self.states[self.state]()
        pass

    def connect(self):
        self.tcp_proto.syn(self.destination_router_id)
        self.state = TCPStateMachine.THREE_WAY_HANDSHAKE_SYN_ACK

    # listen for all incoming messages, drop all except TCP.SYN
    def three_way_handshake_syn_listen(self):
        packet = self.tcp_proto.receive_segment()
        if packet is not None and packet.type == TCPPacket.SYN:
            print("syn handler %s " % self.tcp_proto.router.id)
            self.destination_router_id = packet.src_router_id
            self.tcp_proto.ack(packet.src_router_id)
            self.tcp_proto.syn(packet.src_router_id)
            self.state = TCPStateMachine.THREE_WAY_HANDSHAKE_ACK

    # Receive 3WHS ACK only
    # drop any other packets and wait for SYN again
    def three_way_handshake_ack(self):
        packet = self.tcp_proto.receive_segment()
        if packet is not None and packet.type == TCPPacket.ACK:
            print("ack handler %s " % self.tcp_proto.router.id)
            self.connection_established = True
            self.state = TCPStateMachine.IDLE
        else:
            self.state = TCPStateMachine.IDLE

    def three_way_handshake_syn_ack(self):
        packet = self.tcp_proto.receive_segment()
        if packet is not None and packet.type == TCPPacket.ACK:
            print("syn_ack handler %s " % self.tcp_proto.router.id)
            packet = self.tcp_proto.receive_segment()
            if packet is not None and packet.type == TCPPacket.SYN:
                self.tcp_proto.ack(packet.src_router_id)
                self.state = TCPStateMachine.IDLE
                self.connection_established = True

        else:
            self.state = TCPStateMachine.CONNECT

    # Receive Data ACK only
    def ack(self):
        packet = self.tcp_proto.receive_segment()
        print("data ack handler")
        if packet is not None and packet.type == TCPPacket.ACK:
            self.tcp_proto.confirm_delivery()
            # print("data_left %s" % self.tcp_proto.data_left)
            if self.tcp_proto.data_left > 0:
                self.state = TCPStateMachine.TRANSMIT
            else:
                self.state = TCPStateMachine.IDLE
                self.transmission_done = True
        else:
            self.state = TCPStateMachine.RETRANSMIT

    # Transmit segment and wait for ack
    def transmit_segment(self):
        print("transmit segment %s " % self.destination_router_id)
        self.tcp_proto.transmit_message(self.destination_router_id)
        self.state = TCPStateMachine.ACKNOWLEDGE
        pass

    def retransmit_segment(self):
        # print("retransmit")
        pass

    def receive_segment(self):
        packet = self.tcp_proto.receive_segment()
        if packet is not None and packet.type == TCPPacket.DATA:
            print("receive %s" % packet.message_size)
            self.tcp_proto.ack(packet.src_router_id)
            self.state = TCPStateMachine.IDLE
        pass

    def more_data(self):
        return not self.transmission_done

