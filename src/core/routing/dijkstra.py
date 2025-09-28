from queue import PriorityQueue

from src.core.routing.routing import RoutingStrategy


class DijkstraAlgorithm(RoutingStrategy):

    def __init__(self, router, link_state_db):
        self.link_state_db = link_state_db.copy()
        self.link_state_db[router.id] = router.link_state_db
        self.src = router

    def calculate_cost(self, connection):
        return connection.weight

    def relax(self, connection):

        pass

    def find_optimal_path(self, dest_router_id):
        costs = {lsdb:float('inf') for lsdb in self.link_state_db}
        costs[self.src.id] = 0
        visited = set()
        queue = PriorityQueue()
        queue.put((costs[self.src.id], self.src.id))
        for r in self.link_state_db:
            queue.put((float('inf'), r))
        connections = {self.src.id:None}
        while not queue.empty():
            while not queue.empty():
                item = queue.get()
                print(item)
                if item[1] not in visited:
                    break
            else:
                print("empty queue")
                break
            visited.add(item[1])
            if item[1] == dest_router_id:
                print("dest router")
                break

            lsdb = next(c for c in self.link_state_db if c == item[1])
            print("lsdb %s size %s" % (lsdb, len(self.link_state_db[lsdb].neighbours)))
            for connection in self.link_state_db[lsdb].neighbours:
                neighbor = connection.get_connected_router(item[1]).id
                if neighbor in visited:
                    print("already visited %s" % neighbor)
                    continue
                old = costs[neighbor]
                new = costs[item[1]] + connection.weight
                print("new %s" % new)
                print("old %s" % old)
                if new < old:
                    queue.put((new, neighbor))
                    costs[neighbor] = new
                    connections[neighbor] = connection
                    print(connections)
        print("found %s" % (len(connections)))
        print(connections)
        r = dest_router_id
        ret = {}
        if dest_router_id not in connections:
            return None
        sum_weight = 0
        while r is not None:
            print(r)
            conn = connections[r]
            r = conn.get_connected_router(r).id if conn is not None else None
            if r is not None:
                ret[r] = conn
                sum_weight = sum_weight + conn.weight

        return ret, sum_weight