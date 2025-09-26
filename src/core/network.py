import random

from src.core.channel import Channel
from src.core.router import Router


class Network:
    def __init__(self):
        self.routers = []
        self.serial = 0
        pass

    def get_router_by_id(self, id):
        for router in self.routers:
            if router.id == id:
                return router
        return None

    def add_router(self):
        router = Router(self.serial)
        self.serial = self.serial + 1
        self.routers.append(router)
        return router.id

    def add_connection(self, r1, r2, weight, duplex):
        r = []
        if r1 == r2:
            return
        for router in self.routers:
            if router.id == r1 or router.id == r2:
                r.append(router)
        if len(r) == 2:
            connection = Channel(r[0], r[1], duplex, weight)
            r[0].add_connection(connection, r[1].id)
            r[1].add_connection(connection, r[0].id)
            r[0].advertise_links(r[0].link_state_db)
            r[1].advertise_links(r[1].link_state_db)

            for _r in r:
                if len(_r.connections) == 1:
                    _r.request_link_state_db()
        pass

    def generate(self):
        self.serial = 0
        self.routers = []
        routers_num = random.randint(25, 30)
        for i in range(0, routers_num):
            self.add_router()
        touched = [False] * (routers_num + 1)
        while not all(touched):
            r1 = random.randint(0, routers_num)
            r2 = (r1 + random.randint(0, 5)) % routers_num
            if r1 == r2:
                continue
            touched[r1] = True
            touched[r2] = True
            weight = random.randint(0, routers_num)

            self.add_connection(r1, r2, weight, True if random.randint(0, 1) else False)

    def get_avg_network_power(self):
        avg_network_power = 0
        for router in self.routers:
            avg_network_power += len(router.connections)

        avg_network_power /= len(self.routers) if len(self.routers) else 1
        return avg_network_power