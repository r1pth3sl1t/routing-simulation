class RoutingRecord:
    def __init__(self, dest, gateway, weight):
        self.dest = dest
        self.gateway = gateway
        self.weight = weight
        pass

class RoutingTable:
    def __init__(self):
        self.records = {}

    def add_record(self, dest, gateway, weight):
        self.records[dest] = RoutingRecord(dest, gateway, weight)

    # Remove all records related to the dest router, including records where it is a gateway
    def remove_record(self, dest):
        if dest in self.records:
            del self.records[dest]
        gw_keys = []
        for record in self.records:
            if self.records[record].gateway == dest:
                gw_keys.append(record)

        for record in gw_keys:
            del self.records[record]

    def contains(self, dest, gateway, weight):
        for record in self.records:

            if record.dest == dest and record.gateway == gateway and record.weight == weight:
                return True

        return False

    def get_gateway(self, dest_router_id):
        if dest_router_id in self.records:
            return self.records[dest_router_id]
        return None