import random

from src.core import network
from src.core.entities.network.packets.ip_packet import IPLayerPacket
from src.core.entities.router import Router


class Channel(object):
    def __init__(self, r1: Router, r2: Router, duplex, weight):
        self.duplex = duplex
        self.weight = weight
        self.r1 = r1
        self.r2 = r2
        pass

    def get_connected_router(self, r):
        return self.r1 if self.r2.id == r else self.r2

    def equals(self, r1, r2):
        return (self.r1.id == r1 and self.r2.id == r2) or (self.r1.id == r2 and self.r2.id == r1)


    @staticmethod
    def drop_with_probability(probability, message):
        return random.random() < probability * message.msg_size / network.MTU

    def transmit(self, src, message: IPLayerPacket):
        jitter = message.msg_size * self.weight
        if self.duplex == 0:
            jitter *= 2

        # Drop the packet with certain error rate depending on packet size:
        # the smaller the packet -> less drop probability
        if self.drop_with_probability(network.ERROR_RATE, message):
            return
        jitter *= 0.000001
        message.transport_layer_packet.inc_jitter(jitter)
        self.get_connected_router(src).receive(message)
