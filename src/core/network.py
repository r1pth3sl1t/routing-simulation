import csv
import os
import random

from src.core.entities.channel import Channel
from src.core.entities.network.packets.ip_packet import IPLayerPacket
from src.core.entities.network.packets.data import RawData
from src.core.entities.network.proto.tcp import TransmissionControlProtocol
from src.core.entities.network.proto.tcp_sm import TCPStateMachine
from src.core.entities.network.proto.udp import UserDatagramProtocol
from src.core.entities.router import Router
from src.core.utils.benchmark_stats import BenchmarkStats
from src.core.utils.transmit_stats import TransmitStats

DEFAULT_MTU = 1500
DEFAULT_ERROR_RATE = 0.02

MTU = 1500
ERROR_RATE = 0.02
TCP = 0
UDP = 1
BENCHMARK_CFG = {"MTU": "../../tests/mtu.csv",
                 "ERR_RATE": "../../tests/err_rate.csv",
                 "MESSAGE_SIZE": "../../tests/msg_size.csv"}

class Network:
    def __init__(self):
        self.routers = {}
        self.serial = 0
        self.transmission_in_progress = False
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
            if c1 and c2:
                r[0].advertise_links(None)
                r[1].advertise_links(None)

                for _r in r:
                    _r.request_link_state_db()

                return True
        return False

    def remove_connection(self, r1, r2):
        router = self.get_router_by_id(r1)
        connected_router = self.get_router_by_id(r2)
        router.remove_connection(r2, False)
        router.advertise_links(None)
        connected_router.advertise_links(None)

    def generate(self):
        self.serial = 0
        self.routers = {}
        routers_num = 29

        for i in range(0, routers_num):
            self.add_router()

        def generate_subnet(index_from, index_to):
            for i in range(index_from, index_to):
                for j in range(index_from, index_to):
                    weight = random.randint(1, routers_num)
                    if random.random() < 0.1:
                        self.add_connection(i, j, weight, random.randint(0, 1))

                for j in range(index_from, index_to):
                    if not self.get_router_by_id(j).connections or len(self.get_router_by_id(j).connections) < 2:

                        self.add_connection(j, random.randint(index_from, index_to - 1), random.randint(1, routers_num), random.randint(0, 1))

        generate_subnet(0, 10)
        generate_subnet(10, 20)
        generate_subnet(20, routers_num)
        self.add_connection(9, 10, 1, 1)
        self.add_connection(19, 20, 1, 1)
        self.add_connection(29, 0, 1, 1)


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

    def get_l3_stats(self, router_id):
        r = self.get_router_by_id(router_id)
        return r.l3_stats

    def transmit_message(self, message_size, protocol, src, dst):
        if self.transmission_in_progress:
            return None, None

        self.transmission_in_progress = True
        src_router = self.get_router_by_id(src)
        dst_router = self.get_router_by_id(dst)
        message = RawData(message_size)

        if protocol == TCP:
            t1 = TCPStateMachine(TransmissionControlProtocol(src_router, message, MTU - IPLayerPacket.HEADER_SIZE))
            t2 = TCPStateMachine(TransmissionControlProtocol(dst_router, message))
            t1.set_dest_router_id(dst)
            t1.init_connect()

            while not (t1.connection_established or t2.connection_established):
                t1.next()
                t2.next()
            t1.init_transmit()

            while t1.more_data():
                t1.next()
                t2.next()

            self.transmission_in_progress = False
            return TransmitStats(src_router.l3_stats,
                          t1.tcp_proto.l4_stats,
                          dst_router.l3_stats,
                          t2.tcp_proto.l4_stats,
                          message_size, MTU, "TCP", ERROR_RATE)
        else:
            u1 = UserDatagramProtocol(src_router, message, MTU - IPLayerPacket.HEADER_SIZE)
            u2 = UserDatagramProtocol(dst_router, message)
            u1.transmit_message(dst)
            u2.receive_message()
            self.transmission_in_progress = False
            return TransmitStats(src_router.l3_stats,
                          u1.l4_stats,
                          dst_router.l3_stats,
                          u2.l4_stats,
                          message_size, MTU, "UDP", ERROR_RATE)

    def benchmark(self, src, dst, benchmark_type):
        src_router = self.get_router_by_id(src)
        dst_router = self.get_router_by_id(dst)
        global MTU
        global ERROR_RATE
        with open(os.path.join(__file__, BENCHMARK_CFG[benchmark_type]), newline='') as cfg:
            cfg_reader = csv.DictReader(cfg)
            benchmark_stats = BenchmarkStats()

            for row in cfg_reader:
                MTU = int(row['mtu'])
                ERROR_RATE = float(row['err_rate'])
                message_size = int(row['message_size'])
                proto = row['proto']
                benchmark_stats.add_record(self.transmit_message(message_size, 0 if proto == "TCP" else 1, src, dst))

        MTU = DEFAULT_MTU
        ERROR_RATE = DEFAULT_ERROR_RATE
        return benchmark_stats
