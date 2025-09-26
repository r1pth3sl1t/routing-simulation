from numpy.ma.core import append

from src.core.link_state_db import LinkStateDB
from src.core.routing_table import RoutingTable


class Router(object):
    def __init__(self, id):
        self.id = id
        self.routing_table = RoutingTable()
        self.connections = []
        self.link_state_db = None
        self.topology = []
        pass

    def add_connection(self, channel, dest):
        self.connections.append(channel)
        self.routing_table.add_record(dest, dest, channel.weight)

        pass

    def advertise_links(self, link_state_db):
        if self.link_state_db is None:
            self.link_state_db = LinkStateDB(self)

        if link_state_db is None:
            link_state_db = self.link_state_db

        # do not add links state DB if router already has a valid record
        for links in self.topology:
            if links.router.id == link_state_db.router.id and len(links.neighbours) == len(link_state_db.neighbours):
                return
        if self.id != link_state_db.router.id:
            self.topology.append(link_state_db)

        # propagate link state DB between all routers
        for connection in self.connections:
            router = connection.r2 if connection.r1 == self else connection.r1

            router.advertise_links(link_state_db)

    def request_link_state_db(self):
        for connection in self.connections:
            router = connection.r2 if connection.r1 == self else connection.r1
            lsdb = router.topology
            for link_state_db in lsdb:
                if (not any(r.router.id == link_state_db.router.id for r in self.topology)
                        and link_state_db.router.id != self.id):
                    self.topology.append(link_state_db)
