from dash import dash_table

class StatsTableGUIComponent:
    def __init__(self, stats):
        self.stats = stats

    def tx_stats_to_dict(self):
        tx_stats = {
            'TYPE': 'TX',
            'OVERALL': self.stats.tx_stats.overall_bytes,
            'DATA': self.stats.tx_stats.data_bytes,
            'MGMT': self.stats.tx_stats.mgmt_bytes
        }
        return tx_stats

    def rx_stats_to_dict(self):
        rx_stats = {
            'TYPE': 'RX',
            'OVERALL': self.stats.rx_stats.overall_bytes,
            'DATA': self.stats.rx_stats.data_bytes,
            'MGMT': self.stats.rx_stats.mgmt_bytes
        }
        return rx_stats

    def to_html(self):
        records = [self.tx_stats_to_dict(), self.rx_stats_to_dict()]
        return dash_table.DataTable(
            records,
            columns=[
                {'name': 'TYPE', 'id': 'TYPE'},
                {'name': 'OVERALL', 'id': 'OVERALL'},
                {'name': 'DATA', 'id': 'DATA'},
                {'name': 'MGMT', 'id': 'MGMT'}
            ],
            style_table={
                'maxHeight': '300px',
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
                'position': 'sticky',
                'top': 0,
                'zIndex': 1
            },
            style_data_conditional=[
                {'if': {'row_index': 'odd'}, 'backgroundColor': '#f9f9f9'},
                {'if': {'row_index': 'even'}, 'backgroundColor': '#ffffff'},
                {'if': {'state': 'active'}, 'backgroundColor': '#e0f7fa', 'border': '1px solid #0097a7'}
            ],
            page_action='none'
        )