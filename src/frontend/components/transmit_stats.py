from dash import html, dash_table

from src.frontend.components.stats_table import StatsTableGUIComponent


class TransmitStatsGUIComponent:
    def __init__(self, transmit_stats):
        self.transmit_stats = transmit_stats
        pass

    def overall_stats_to_dict(self):
        return [{
            "Втрати":  self.transmit_stats.get_error_rate(),
            "Перевідправлень": self.transmit_stats.get_retransmits(),
            "Час": self.transmit_stats.get_overall_time(),
        }]

    def overall_stats_to_html(self):
        return dash_table.DataTable(
            self.overall_stats_to_dict(),
            columns=[
                {'name': 'Втрати', 'id': 'Втрати'},
                {'name': 'Перевідправлень', 'id': 'Перевідправлень'},
                {'name': 'Час', 'id': 'Час'},
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

    def to_html(self):
        return html.Div([
            StatsTableGUIComponent(self.transmit_stats.tx_l4_stats.stats).to_html(),
            StatsTableGUIComponent(self.transmit_stats.rx_l4_stats.stats).to_html(),
            self.overall_stats_to_html()],
            style={
                "maxHeight": "250px",
                "overflowY": "auto",
                "border": "1px solid #ccc",
                "borderRadius": "6px",
                "marginBottom": "15px",
                "padding": "4px",
                "backgroundColor": "#fff",
                "boxShadow": "2px 2px 6px rgba(0,0,0,0.1)"
            }
        )
