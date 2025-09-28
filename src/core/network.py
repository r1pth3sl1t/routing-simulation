import random

from src.core.entities.channel import Channel
from src.core.entities.router import Router


class Network:
    def __init__(self):
        self.routers = []
        self.serial = 0
        pass

    def get_router_by_id(self, router_id):
        for router in self.routers:
            if router.id == router_id:
                return router
        return None

    def add_router(self):
        router = Router(self.serial)
        self.serial = self.serial + 1
        self.routers.append(router)
        return router.id

    def remove_router(self, r):
        router = self.get_router_by_id(r)
        print(router.id)
        print(len(router.connections))
        connections = [c.get_connected_router(r).id for c in router.connections]

        for connection in connections:
            self.remove_connection(r, connection)
        self.routers.remove(router)

    def add_connection(self, r1, r2, weight, duplex):
        r = []
        if r1 == r2:
            return False
        for router in self.routers:
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
        self.routers = []
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
        for router in self.routers:
            avg_network_power += len(router.connections)

        avg_network_power /= len(self.routers) if len(self.routers) else 1
        return avg_network_power

    def find_shortest(self, src, dest):
        router = self.get_router_by_id(src)
        connections, _ = router.find_shortest_path(dest)
        if connections is None:
            return None

        ret = {}
        for c in connections:
            print(c)
            conn = connections[c]
            ret[c] = conn.get_connected_router(c).id if conn is not None else None

        return ret