import random

from src.core.entities.network.packets.tcp_packet import TCPPacket
from src.core.entities.network.stats.l4_stats import L4Stats


class TCPStateMachine:
    IDLE = 0
    CONNECT = 1
    THREE_WAY_HANDSHAKE_SYN_ACK = 4
    THREE_WAY_HANDSHAKE_ACK = 6
    TRANSMIT = 7
    RETRANSMIT = 8
    ACKNOWLEDGE = 9
    ACKNOWLEDGE_WAIT = 10
    FIN = 11

    def __init__(self, tcp_proto, connection_retries=3):
        self.state = self.IDLE
        self.tcp_proto = tcp_proto
        self.connection_established = False
        self.syn_received = False
        self.destination_router_id = -1
        self.connection_retries = connection_retries
        self.disconnect_in_progress = False
        self.transmission_done = False
        self.packet = None
        self.states = {
            TCPStateMachine.IDLE: self.idle,
            TCPStateMachine.THREE_WAY_HANDSHAKE_ACK: self.three_way_handshake_ack,
            TCPStateMachine.THREE_WAY_HANDSHAKE_SYN_ACK: self.three_way_handshake_syn_ack,
            TCPStateMachine.TRANSMIT: self.transmit_segment,
            TCPStateMachine.CONNECT: self.connect,
            TCPStateMachine.RETRANSMIT: self.retransmit_segment,
            TCPStateMachine.ACKNOWLEDGE: self.ack
        }

    def consume_packet(self):
        if self.packet is None:
            self.packet = self.tcp_proto.receive_message()

        return self.packet

    def release_packet(self):
        self.packet = None

    def set_dest_router_id(self, dst):
        if dst != self.tcp_proto.router.id:
            self.destination_router_id = dst
        else:
            self.transmission_done = True

    def init_connect(self):
        if self.destination_router_id >= 0:
            self.state = TCPStateMachine.CONNECT

    def init_transmit(self):
        if self.destination_router_id >= 0 and self.connection_established:
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
        packet = self.consume_packet()
        if packet is not None and packet.type == TCPPacket.SYN:
            self.destination_router_id = packet.src_router_id
            self.tcp_proto.syn_ack(packet.src_router_id)
            self.state = TCPStateMachine.THREE_WAY_HANDSHAKE_ACK
            self.release_packet()
            self.syn_received = True
        elif self.syn_received:
            self.tcp_proto.syn_ack(self.destination_router_id)
            self.state = TCPStateMachine.THREE_WAY_HANDSHAKE_ACK
            self.release_packet()
        else:
            self.state = TCPStateMachine.IDLE

    # Receive 3WHS ACK only
    # drop any other packets and wait for SYN again
    def three_way_handshake_ack(self):
        packet = self.consume_packet()
        if packet is not None and packet.type == TCPPacket.ACK:
            self.connection_established = True
            self.state = TCPStateMachine.IDLE
            self.release_packet()
        else:
            self.three_way_handshake_syn_listen()

    def three_way_handshake_syn_ack(self):
        packet = self.consume_packet()
        if packet is not None and packet.type == TCPPacket.SYN_ACK:
            self.tcp_proto.ack(packet.src_router_id)
            self.connection_established = True
            self.state = TCPStateMachine.IDLE
            self.release_packet()
        else:
            self.state = TCPStateMachine.CONNECT

    # Receive Data ACK only
    def ack(self):
        packet = self.consume_packet()
        if packet is not None and packet.type == TCPPacket.ACK:
            self.tcp_proto.confirm_delivery()
            self.state = TCPStateMachine.TRANSMIT
            if self.disconnect_in_progress:
                self.transmission_done = True

            self.release_packet()
        else:
            # Prevent client ESTABLISHED <---> server SYN RECEIVED - from
            # If client did not get SYN-ACK packet, it means that segment wasn't delivered
            self.three_way_handshake_syn_ack()
            if self.state == TCPStateMachine.CONNECT:
                self.state = TCPStateMachine.RETRANSMIT
            elif self.state == TCPStateMachine.IDLE:
                self.state = TCPStateMachine.RETRANSMIT

    # Transmit segment and wait for ack
    def transmit_segment(self):
        if self.tcp_proto.data_left > 0:
            self.tcp_proto.transmit_message(self.destination_router_id)
        else:
            self.disconnect_in_progress = True
            self.tcp_proto.fin(self.destination_router_id)
        self.state = TCPStateMachine.ACKNOWLEDGE
        pass

    # Retransmit is pretty the same state as transmit, it will send the "exact same"
    # packet because its delivery wasn't confirmed on the TX side
    def retransmit_segment(self):
        self.tcp_proto.l4_stats.retransmits += 1
        self.transmit_segment()
        pass

    def receive_segment(self):
        packet = self.consume_packet()
        if packet is not None:
            if packet.type == TCPPacket.DATA:
                #if random.randint(1, 10) > 7:
                self.tcp_proto.ack(packet.src_router_id)
                self.state = TCPStateMachine.IDLE
            elif packet.type == TCPPacket.FIN:
                self.disconnect_in_progress = True
                self.tcp_proto.ack(packet.src_router_id)
            elif packet.type == TCPPacket.ACK:
                pass

            self.release_packet()
        pass

    def more_data(self):
        return not self.transmission_done

