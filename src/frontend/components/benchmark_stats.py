from dash import dash_table
from dash.dash_table import FormatTemplate
from dash.dash_table.Format import Format

from src.frontend.components.stats_table import StatsTableGUIComponent
from src.frontend.components.transmit_stats import TransmitStatsGUIComponent


class BenchmarkStatsGUIComponent:

    def benchmark_stats_to_dict(self):
        records = []
        for bc in self.benchmark_stats.transmit_stats:
            r = TransmitStatsGUIComponent(bc).overall_stats_to_dict()
            r.update({
                'MTU': bc.mtu,
                'proto': bc.proto,
                'MSG_SIZE': bc.message_size,
                'MGMT_RATIO': bc.get_mgmt_bytes_ratio() * 100
            })
            r.update(StatsTableGUIComponent(bc.tx_l4_stats.stats).tx_stats_to_dict())
            records.append(r)

        return records

    def __init__(self, benchmark_stats):
        self.benchmark_stats = benchmark_stats

    def to_html(self):
        return dash_table.DataTable(
            self.benchmark_stats_to_dict(),
            columns=[
                {'name': 'MTU', 'id': 'MTU'},
                {'name': 'Протокол', 'id': 'proto'},
                {'name': 'Розмір повідомлення', 'id': 'MSG_SIZE'},
                {'name': 'Байт даних', 'id': 'DATA'},
                {'name': 'Служб. трафік', 'id': 'MGMT_RATIO', "type": "numeric", 'format': Format(precision=2, scheme='f')},
                {'name': 'Втрати', 'id': 'Втрати', "type": "numeric", 'format': Format(precision=2, scheme='f')},
                {'name': 'Перевідправлень', 'id': 'Перевідправлень'},
                {'name': 'Час', 'id': 'Час', "type": "numeric", 'format': Format(precision=2, scheme='f')},
            ],
            style_table={
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
                'zIndex': 1,
                'whiteSpace': 'normal',
                'height': 'auto',
                'overflow': 'visible'
            },
            style_data_conditional=[
                {'if': {'row_index': 'odd'}, 'backgroundColor': '#f9f9f9'},
                {'if': {'row_index': 'even'}, 'backgroundColor': '#ffffff'},
                {'if': {'state': 'active'}, 'backgroundColor': '#e0f7fa', 'border': '1px solid #0097a7'}
            ],
            page_action='none'
        )