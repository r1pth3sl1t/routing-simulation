from dash import html


class RoutingRecord:
    def __init__(self, dest, gateway, weight):
        self.dest = dest
        self.gateway = gateway
        self.weight = weight
        pass

    def to_html(self):
        return html.P("Призначення: %s Шлюз: %s Метрика: %s" % (self.dest, self.gateway, self.weight))

class RoutingTable:
    def __init__(self):
        self.records = []

    def add_record(self, dest, gateway, weight):
        self.records.append(RoutingRecord(dest, gateway, weight))

    def to_html(self):
        records = []
        for record in self.records:
            records.append(record.to_html())
        return html.Div(records)

    def contains(self, dest, gateway, weight):
        for record in self.records:

            if record.dest == dest and record.gateway == gateway and record.weight == weight:
                return True

        return False

    def get_link_state_db(self):
        lsdb = []
        for record in self.records:
            if record.dest == record.gateway:
                lsdb.append(record.dest)

        return lsdb