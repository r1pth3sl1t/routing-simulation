from src.core.entities.link_state_db import LinkStateDB
from src.core.entities.routing_table import RoutingTable
from src.core.routing.dijkstra import DijkstraAlgorithm


class Router(object):
    def __init__(self, router_id):
        self.id = router_id
        self.routing_table = RoutingTable()
        self.connections = []
        self.link_state_db = None
        self.topology = {}
        pass

    def add_connection(self, channel, dest):
        for connection in self.connections:
            if connection.get_connected_router(self.id).id == dest:
                return False
        self.connections.append(channel)
        self.routing_table.add_record(dest, dest, channel.weight)

        return True



    def remove_connection(self, dest, router_disconnected):
        connection = next(c for c in self.connections if c.get_connected_router(self.id).id == dest)
        self.connections.remove(connection)
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
        for connection in self.connections:
            router = connection.get_connected_router(self.id)
            if router.id != link_state_db.router.id:
                router.advertise_links(link_state_db.copy())


    def request_link_state_db(self):
        for connection in self.connections:
            router = connection.get_connected_router(self.id)
            lsdb = router.topology
            for link_state_db in lsdb:
                if lsdb[link_state_db].router.id != self.id:
                    self.advertise_links(lsdb[link_state_db])
                    self.topology[link_state_db] = lsdb[link_state_db].copy()

    def find_shortest_path(self, router):
        routing_strategy = DijkstraAlgorithm(self, self.topology)
        return routing_strategy.find_optimal_path(router)

    def fillup_routing_table(self):
        for r in self.topology:
            path, sum_weight = self.find_shortest_path(r)
            self.routing_table.add_record(r, path[self.id].get_connected_router(self.id).id, sum_weight)
