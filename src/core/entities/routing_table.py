from dash import html, dash_table


class RoutingRecord:
    def __init__(self, dest, gateway, weight):
        self.dest = dest
        self.gateway = gateway
        self.weight = weight
        pass

    def to_html(self):
        return {'Призначення': self.dest, 'Шлюз': self.gateway, 'Метрика': self.weight}

class RoutingTable:
    def __init__(self):
        self.records = {}

    def add_record(self, dest, gateway, weight):
        self.records[dest] = RoutingRecord(dest, gateway, weight)

    def to_html(self):
        records = []
        for record in self.records:
            records.append(self.records[record].to_html())
        return dash_table.DataTable(records, style_cell={"textAlign": "center", "padding": "6px"}, id='router-table')

    def contains(self, dest, gateway, weight):
        for record in self.records:

            if record.dest == dest and record.gateway == gateway and record.weight == weight:
                return True

        return False