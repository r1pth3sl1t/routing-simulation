import random

from src.core.entities.channel import Channel
from src.core.entities.network.packets.IPLayerPacket import IPLayerPacket
from src.core.entities.network.packets.data import RawData
from src.core.entities.network.packets.tcp_packet import TCPPacket
from src.core.entities.network.proto.proto import TransportLayerProtocol
from src.core.entities.network.proto.tcp import TransmissionControlProtocol
from src.core.entities.network.proto.tcp_sm import TCPStateMachine
from src.core.entities.router import Router

MTU = 1500
TCP = 0
UDP = 1

class Network:
    def __init__(self):
        self.routers = {}
        self.serial = 0
        pass

    def get_router_by_id(self, router_id):
        if router_id in self.routers:
            return self.routers[router_id]
        return None

    def add_router(self):
        router = Router(self.serial)
        self.routers[self.serial] = router
        self.serial = self.serial + 1
        return router.id

    def remove_router(self, r):
        router = self.get_router_by_id(r)
        connections = [c.get_connected_router(r).id for c in router.connections]

        for connection in connections:
            self.remove_connection(r, connection)

        del self.routers[r]

    def add_connection(self, r1, r2, weight, duplex):
        r = []
        if r1 == r2:
            return False
        for router in self.routers.values():
            if router.id == r1 or router.id == r2:
                r.append(router)

        if len(r) == 2:
            connection = Channel(r[0], r[1], duplex, weight)
            c1 = r[0].add_connection(connection, r[1].id)
            c2 = r[1].add_connection(connection, r[0].id)
            #print("create %s %s" % (r1, r2))
            if c1 and c2:
                r[0].advertise_links(None)
                r[1].advertise_links(None)

                for _r in r:
                    _r.request_link_state_db()

                return True
        return False

    def remove_connection(self, r1, r2):
        router = self.get_router_by_id(r1)
        router.remove_connection(r2, False)
        router.advertise_links(None)

    def generate(self):
        self.serial = 0
        self.routers = {}
        routers_num = random.randint(25, 30)
        for i in range(0, routers_num):
            self.add_router()
        touched = [False] * (routers_num + 1)
        while not all(touched):
            r1 = random.randint(0, routers_num)
            r2 = (r1 + random.randint(0, 3)) % routers_num
            if r1 == r2:
                continue
            touched[r1] = True
            touched[r2] = True
            weight = random.randint(1, routers_num)
            self.add_connection(r1, r2, weight, random.randint(0, 1))

    def get_avg_network_power(self):
        avg_network_power = 0
        for router in self.routers.values():
            avg_network_power += len(router.connections)

        avg_network_power /= len(self.routers) if len(self.routers) else 1
        return avg_network_power

    def find_shortest(self, src, dest):
        router = self.get_router_by_id(src)
        connections = router.find_shortest_path(dest)
        if connections is None:
            return None

        ret = {}
        for c in connections:
            conn = connections[c]
            ret[c] = conn.get_connected_router(c).id if conn is not None else None

        return ret

    def transmit_message(self, message_size, protocol, src, dst):
        src_router = self.get_router_by_id(src)
        dst_router = self.get_router_by_id(dst)
        #print("dest router: %s" % dst)
        #transport_layer_msg = TCPPacket(src, dst, 1472, TCPPacket.DATA)
        #print("transport_layer_msg: %s" % transport_layer_msg.get_message_size())
        #src_router.transmit(dst, transport_layer_msg)
        t1 = TCPStateMachine(TransmissionControlProtocol(src_router, RawData(10000), MTU - IPLayerPacket.HEADER_SIZE))
        t2 = TCPStateMachine(TransmissionControlProtocol(dst_router, None))
        t1.set_dest_router_id(dst)
        t1.init_connect()
        for i in range(0, 5):
            t1.next()
            t2.next()
        t1.init_transmit()
        print(t1.more_data())
        while t1.more_data():
            t1.next()
            t2.next()
        print("done!")
        # if protocol == TCP:
        #    tcp = TransportLayerProtocol(router)
        #    tcp.send_message(RawData(message_size), dst)
        #else:
        #    pass

