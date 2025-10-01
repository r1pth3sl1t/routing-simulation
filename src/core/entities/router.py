from src.core import network
from src.core.entities.link_state_db import LinkStateDB
from src.core.entities.network.packets.IPLayerPacket import IPLayerPacket
from src.core.entities.network.packets.packet import TransportLayerPacket
from src.core.entities.routing_table import RoutingTable
from src.core.routing.dijkstra import DijkstraAlgorithm


class Router(object):

    def __init__(self, router_id):
        self.id = router_id
        self.routing_table = RoutingTable()
        self.connections = {}
        self.link_state_db = None
        self.topology = {}
        self.rxq = []
        self.txq = []
        self.frags = {}
        pass

    def add_connection(self, channel, dest):
        for connection in self.connections.values():
            if connection.get_connected_router(self.id).id == dest:
                return False
        self.connections[dest] = channel
        self.routing_table.add_record(dest, dest, channel.weight)

        return True



    def remove_connection(self, dest, router_disconnected):
        connection = next(c for c in self.connections if c.get_connected_router(self.id).id == dest)
        del self.connections[connection]
        if not router_disconnected:
            connection.get_connected_router(self.id).remove_connection(self.id, True)

        pass

    def advertise_links(self, link_state_db):
        self.link_state_db = LinkStateDB(self)

        if link_state_db is None:
            link_state_db = self.link_state_db

        # do not add links state DB if router already has a valid record
        if link_state_db.router.id in self.topology and len(self.topology[link_state_db.router.id].neighbours) == len(link_state_db.neighbours):
            return

        if self.id != link_state_db.router.id:
            self.topology[link_state_db.router.id] = link_state_db.copy()

        # propagate link state DB between all routers except source of packet
        for connection in self.connections.values():
            router = connection.get_connected_router(self.id)
            if router.id != link_state_db.router.id:
                router.advertise_links(link_state_db.copy())


    def request_link_state_db(self):
        for connection in self.connections.values():
            router = connection.get_connected_router(self.id)
            lsdb = router.topology
            for link_state_db in lsdb:
                if lsdb[link_state_db].router.id != self.id:
                    self.advertise_links(lsdb[link_state_db])
                    self.topology[link_state_db] = lsdb[link_state_db].copy()

    def find_shortest_path(self, router):
        if router not in self.topology:
            return None
        routing_strategy = DijkstraAlgorithm(self, self.topology)
        path, sum_weight = routing_strategy.find_optimal_path(router)
        self.routing_table.add_record(router, path[self.id].get_connected_router(self.id).id, sum_weight)
        return path

    def fillup_routing_table(self):
        for r in self.topology:
            self.find_shortest_path(r)

    def transmit(self, message: TransportLayerPacket):
        dest = message.dest_router_id
        message_size = message.get_message_size()
        seq_num = IPLayerPacket.next_sequence_number()
        frag_num = 0
        while message_size > 0:
            #print("message_left %s" % message_size)
            more_fragments = 1
            if frag_num == 2:
                frag_num = 5
            if message_size <= network.MTU - IPLayerPacket.HEADER_SIZE:
                more_fragments = 0
            ip_packet = IPLayerPacket(self.id, dest, message, seq_num, frag_num, more_fragments)
            self.forward(ip_packet)
            message_size = message_size - (network.MTU - IPLayerPacket.HEADER_SIZE)
            frag_num += 1

        pass

    def forward(self, packet: IPLayerPacket):
        if self.routing_table.get_gateway(packet.dest) is None:
            self.find_shortest_path(packet.dest)

        record = self.routing_table.get_gateway(packet.dest)
        if record is None:
            return
        self.connections[record.gateway].transmit(self.id, packet)

    def receive(self, packet: IPLayerPacket):
        if packet.dest == self.id:
            #print("rec %s" % packet.more_fragments)
            # simulate reassembly of IP packet on RX side
            if packet.seq_num not in self.frags:
                self.frags[packet.seq_num] = -1
            # Real IP protocol uses fragment offset field to reassemble the packet,
            # but for simulation purposes it is enough to use just idx
            if self.frags[packet.seq_num] == packet.frag_num - 1:
                self.frags[packet.seq_num] += 1
                if packet.more_fragments:
                    return
                else:
                    #print("r %s received %s" % (self.id, len(self.rxq)))
                    self.rxq.append(packet.transport_layer_packet)
                    del self.frags[packet.seq_num]
            else:
                # Drop the whole transport layer packet
                del self.frags[packet.seq_num]
        else:
            self.forward(packet)
        pass

    def pop_transport_layer_packet(self):
        if self.rxq:
            return self.rxq.pop(0)
        return None