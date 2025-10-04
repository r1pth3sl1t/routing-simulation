from dash import dash_table

class RoutingRecordGUIComponent:
    def __init__(self, record):
        self.record = record
        pass

    def to_html(self):
        return {'Призначення': self.record.dest,
                'Шлюз': self.record.gateway,
                'Метрика': self.record.weight}

class RoutingTableGUIComponent:
    def __init__(self, routing_table):
        self.routing_table = routing_table

    def to_html(self):
        records = []
        for record in self.routing_table.records:
            records.append(RoutingRecordGUIComponent(self.routing_table.records[record]).to_html())
        return dash_table.DataTable(records,
            style_table={
                'maxHeight': '250px',
                'overflowY': 'auto',
                'border': '1px solid #ccc',
                'borderRadius': '6px',
            },
            style_cell={
                "textAlign": "center",
                "padding": "6px",
                "whiteSpace": "normal",
                "height": "auto"
            },
            style_header={
                'backgroundColor': '#f0f0f0',
                'fontWeight': 'bold',
                'borderBottom': '2px solid #aaa',
            },
            style_data_conditional=[
                {
                    'if': {'row_index': 'odd'},
                    'backgroundColor': '#f9f9f9'
                },
                {
                    'if': {'row_index': 'even'},
                    'backgroundColor': '#ffffff'
                },
                {
                    'if': {'state': 'active'},  # активная строка при выделении
                    'backgroundColor': '#e0f7fa',
                    'border': '1px solid #0097a7'
                }
            ],
            page_action='none',)
