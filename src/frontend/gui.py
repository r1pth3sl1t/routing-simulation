from dash import Dash, html, dcc, Output, Input, State, no_update
import dash_cytoscape as cyto

from src.core import network
from src.core.network import Network
from src.core.utils.transmit_stats import TransmitStats
from src.frontend.components.routing_table import RoutingTableGUIComponent
from src.frontend.components.stats_table import StatsTableGUIComponent
from src.frontend.components.transmit_stats import TransmitStatsGUIComponent


class MainWindow:

    i = 1

    base_graph_stylesheet = [
                            {
                                'selector': 'edge',
                                'style': {
                                    'label': 'data(weight)',
                                }
                            },
                            {
                                'selector': '[duplex = 0]',
                                'style': {
                                    'line-style': 'dashed'
                                }
                            },
                            {
                                'selector': 'node',
                                'style': {
                                'content': 'data(label)'
                               }
                            },
                            ]

    button_style = {
        'padding': '6px 14px',
        'borderRadius': '6px',
        'border': '1px solid #ccc',
        'backgroundColor': '#f9f9f9',
        'color': '#333',
        'cursor': 'pointer',
        'transition': 'all 0.2s ease-in-out'
    }

    button_style_hover = {
        **button_style,
        'backgroundColor': '#eaeaea',
        'border': '1px solid #bbb'
    }

    def __init__(self):
        self.network = Network()
        self.elements = []
        self.app = Dash(__name__)

        self.app.callback(
            [Output('graph', 'elements', allow_duplicate=True),
             Output('network_power', 'children', allow_duplicate=True)],
            Input('add_connection', 'n_clicks'),
            State('src', 'value'),
            State('dst', 'value'),
            State('weight', 'value'),
            State('duplex', 'value'),
            State('graph', 'elements'),
            prevent_initial_call=True
        )(self.add_connection)

        self.app.callback(
            [Output('graph', 'elements', allow_duplicate=True),
             Output('network_power', 'children', allow_duplicate=True)],
            Input('remove_connection', 'n_clicks'),
            State('graph', 'tapEdge'),
            suppress_callback_exceptions=True,
            prevent_initial_call=True,
        )(self.remove_connection)

        self.app.callback(
            [Output('graph', 'elements', allow_duplicate=True),
             Output('network_power', 'children', allow_duplicate=True)],
            Input('remove_router', 'n_clicks'),
            State('graph', 'tapNode'),
            prevent_initial_call=True,
            suppress_callback_exceptions=True
        )(self.remove_router)

        self.app.callback(
            Output('graph', 'stylesheet', allow_duplicate=True),
            Input('find_shortest', 'n_clicks'),
            State('graph', 'tapNode'),
            State('dst_router', 'value'),
            prevent_initial_call=True,
            suppress_callback_exceptions=True
        )(self.find_shortest)

        self.app.callback(
            Output('node-info', 'children', allow_duplicate=True),
            Input('transmit', 'n_clicks'),
            State('graph', 'tapNode'),
            State('dst_router', 'value'),
            State('message_size', 'value'),
            State('proto', 'value'),
            prevent_initial_call=True,
            suppress_callback_exceptions=True
        )(self.transmit_message)

        self.app.callback(
            Output('node-info', 'children', allow_duplicate=True),
            Input('fillup_routing_table', 'n_clicks'),
            State('graph', 'tapNode'),
            prevent_initial_call=True,
            suppress_callback_exceptions=True
        )(self.fillup_routing_table)

        self.app.callback(
            Output('graph', 'elements', allow_duplicate=True),
            Input('add_router', 'n_clicks'),
            State('graph', 'elements'),
            prevent_initial_call=True
        )(self.add_router)

        self.app.callback(
            [Output('graph', 'elements', allow_duplicate=True),
            Output('network_power', 'elements', allow_duplicate=True)],
            Input('generate_network', 'n_clicks'),
            State('graph', 'elements'),
            prevent_initial_call=True
        )(self.generate_network)

        self.app.callback(
            Output('node-info', 'children', allow_duplicate=True),
            Input('graph', 'tapNode'),
            prevent_initial_call = True
        )(self.display_router_info)
        self.app.callback(
            Output('node-info', 'children', allow_duplicate=True),
            Input('graph', 'tapEdge'),
            prevent_initial_call=True
        )(self.display_connection_info)

        self.app.layout = self.refresh_page


        pass

    def fillup_routing_table(self, n, tap_node):
        if not n:
            return no_update

        data = tap_node['data']
        router = self.network.get_router_by_id(int(data.get('id')))

        router.fillup_routing_table()

        return self.display_router_info(tap_node)

    def add_connection(self, n, src, dst, weight, duplex, elements):
        if not n:
            return no_update
        for node in [src, dst]:
            if not int(node) in self.network.routers:
                return elements, no_update
        c = self.network.add_connection(int(src), int(dst), weight, duplex)
        if c:
            elements.append({'data': {'source': src, 'target': dst, 'weight': weight, 'duplex': duplex}})
            return elements, self.refresh_network_power()

        return no_update

    def remove_connection(self, n, connection):
        if not n:
            return no_update, no_update
        data = connection['data']
        self.network.remove_connection(int(data.get('source')), int(data.get('target')))
        return self.refresh_graph(), self.refresh_network_power()

    def display(self,):
        self.app.run(debug=True)
        pass

    def add_router(self, n, elements):
        if not n:
            return no_update

        router_id = self.network.add_router()
        elements.append({'data': {'id': str(router_id), 'label': str(router_id)}})

        return elements

    def remove_router(self, n, router):
        if not n:
            return no_update, no_update
        data = router['data']
        self.network.remove_router(int(data.get('id')))
        return self.refresh_graph(), self.refresh_network_power()

    def display_router_info(self, tap_node):
        if tap_node is None:
            return no_update

        data = tap_node['data']
        router = self.network.get_router_by_id(int(data['id']))

        # Таблицы
        routing_table_div = html.Div(
            RoutingTableGUIComponent(router.routing_table).to_html(),
            style={
                "maxHeight": "250px",
                "border": "1px solid #ccc",
                "borderRadius": "6px",
                "marginBottom": "10px",
                "padding": "4px",
                "backgroundColor": "#fff",
                "boxShadow": "2px 2px 6px rgba(0,0,0,0.1)"
            }
        )

        stats_table_div = html.Div(
            StatsTableGUIComponent(router.l3_stats.stats).to_html(),
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

        # Панель ввода и кнопок
        controls_div = html.Div([
            dcc.Input(id='dst_router', placeholder='target', value='0',
                      style={
                          "height": "36px",
                          "padding": "6px 10px",
                          "border": "1px solid #ccc",
                          "borderRadius": "6px",
                          "boxSizing": "border-box",
                          "lineHeight": "normal",
                          "fontSize": "14px",
                          "display": "inline-block",
                          "verticalAlign": "middle"
                      }),
            dcc.Input(id='message_size', placeholder='target', value=10000,
                      type='number',
                      style={
                          "height": "36px",
                          "padding": "6px 10px",
                          "border": "1px solid #ccc",
                          "borderRadius": "6px",
                          "boxSizing": "border-box",
                          "lineHeight": "normal",
                          "fontSize": "14px",
                          "display": "inline-block",
                          "verticalAlign": "middle"
                      }),
            dcc.Dropdown(
                id="proto",
                options=[
                    {"label": "TCP", "value": network.TCP},
                    {"label": "UDP", "value": network.UDP},
                ],
                value=network.TCP,
                clearable=False,
                style={
                    "height": "36px",
                    "lineHeight": "36px",
                    "minWidth": "100px",
                    "borderRadius": "6px",
                    "fontSize": "14px",
                    "display": "inline-block",
                    "verticalAlign": "middle"
                },
            ),
            html.Button('Знайти найкоротший шлях до', id='find_shortest', n_clicks=0,
                        style=self.button_style),
            html.Button('Відправити пакет', id='transmit', n_clicks=0,
                        style=self.button_style),
            html.Button('Заповнити таблицю маршрутизації', id='fillup_routing_table', n_clicks=0,
                        style=self.button_style),
            html.Button('Видалити маршрутизатор', id='remove_router', n_clicks=0,
                        style=self.button_style)
        ], style={
            "display": "flex",
            "flexWrap": "wrap",
            "alignItems": "center",
            "gap": "10px",
            "marginBottom": "10px"
        })

        return html.Div([
            html.P(f"Ідентифікатор: {data.get('label')}", style={"fontWeight": "bold", "marginBottom": "10px"}),
            routing_table_div,
            stats_table_div,
            controls_div
        ], style={"padding": "10px", "backgroundColor": "#f9f9f9", "borderRadius": "8px",
                  "boxShadow": "2px 2px 10px rgba(0,0,0,0.1)"})

    def find_shortest(self, n, router, dst_router):
        if not n:
            return no_update
        path = self.network.find_shortest(int(router['data'].get('id')), int(dst_router))
        styles = []
        if path is None:
            return no_update
        for p in path:
            styles.append({
                'selector': f'edge[source = "{p}"][target = "{path[p]}"], edge[source = "{path[p]}"][target = "{p}"]',
                'style': {'line-color': 'green', 'width': 4}
            })
        return self.base_graph_stylesheet + styles

    def transmit_message(self, n, router, dst_router, message_size, proto):
        if not n:
            return no_update
        src_router_id = int(router['data'].get('id'))
        dst_router_id = int(dst_router)
        src_stats, dest_stats = self.network.transmit_message(int(message_size), proto, src_router_id, dst_router_id)
        return [self.display_router_info(router), TransmitStatsGUIComponent(
                                                    TransmitStats(self.network.get_l3_stats(src_router_id),
                                                                  src_stats,
                                                                  self.network.get_l3_stats(dst_router_id),
                                                                  dest_stats,
                                                                  message_size))
                                                    .to_html()]


    def display_connection_info(self, tap_connection):
        if tap_connection is None:
            return no_update
        data = tap_connection['data']
        connection = self.network.get_router_by_id(int(data.get('source'))).connections[int(data.get('target'))]
        return html.Div(
            [
                html.P("Вага: %s" % connection.weight),
                html.P("Дуплекс: %s" % ("Повний" if connection.duplex else "Напівдуплекс")),
                html.Button('Видалити з\'єднання', id='remove_connection', n_clicks=0, style=self.button_style),
             ]
        )

    def generate_network(self, n, elements):
        if not n:
            return elements, no_update

        self.network.generate()
        print("avg", self.network.get_avg_network_power())
        return self.refresh_graph(), self.refresh_network_power()

    def refresh_graph(self):
        elements = []
        for router in self.network.routers.values():
            elements.append({'data': {'id': str(router.id), 'label': str(router.id)}})
            for connection in router.connections.values():
                if connection.r1.id == router.id:
                    elements.append({'data': {'source': str(router.id), 'target': str(connection.r2.id),
                                              'weight': connection.weight, 'duplex': connection.duplex}})

        return elements

    def refresh_network_power(self):
        return html.Span(str(self.network.get_avg_network_power()), id="network_power")

    def refresh_page(self):
        elements = []
        for router in self.network.routers.values():
            elements.append({'data': {'id': str(router.id), 'label': str(router.id)}})
            for connection in router.connections.values():
                if connection.r1.id == router.id:
                    elements.append({'data': {'source': str(router.id), 'target': str(connection.r2.id), 'weight': connection.weight, 'duplex': connection.duplex}})

        return html.Div([
            html.Div([
                cyto.Cytoscape(
                    id='graph',
                    layout={
                        'name': 'cose',
                        'idealEdgeLength': 100,
                        'nodeRepulsion': 4000,
                        'animate': True
                    },
                    style={
                        'width': '60%',
                        'height': '600px',
                        'border': '1px solid #ddd',
                        'borderRadius': '8px',
                        'boxShadow': '0 2px 6px rgba(0,0,0,0.1)',
                        'marginRight': '15px'
                    },
                    elements=elements,
                    stylesheet=self.base_graph_stylesheet,
                ),
                html.Div([
                    html.Div(
                        id='node-info',
                        children="Натисніть на елемент, щоб отримати інформацію",
                        style={
                            'padding': '10px',
                            'border': '1px solid #ddd',
                            'borderRadius': '8px',
                            'backgroundColor': '#fafafa',
                            'height': '580px',
                            'overflowY': 'auto',
                            'boxShadow': '0 2px 6px rgba(0,0,0,0.1)',
                        }
                    ),
                    html.Footer([
                        html.Span("Степінь мережі: "),
                        self.refresh_network_power()
                    ], style={
                        "marginTop": "10px",
                        "padding": "5px 10px",
                        "borderTop": "1px solid #ddd",
                        "color": "#555",
                        "fontSize": "14px"
                    })
                ], style={'flex': 1})
            ], style={
                'display': 'flex',
                'flexDirection': 'row',
                'height': '600px',
                'marginBottom': '20px'
        }),

        html.Div([
            dcc.Input(id='src', placeholder='source', style={
                          "height": "36px",
                          "padding": "6px 10px",
                          "border": "1px solid #ccc",
                          "borderRadius": "6px",
                          "boxSizing": "border-box",
                          "lineHeight": "normal",
                          "fontSize": "14px",
                          "display": "inline-block",
                          "verticalAlign": "middle"
                      }),
            dcc.Input(id='dst', placeholder='target', style={
                          "height": "36px",
                          "padding": "6px 10px",
                          "border": "1px solid #ccc",
                          "borderRadius": "6px",
                          "boxSizing": "border-box",
                          "lineHeight": "normal",
                          "fontSize": "14px",
                          "display": "inline-block",
                          "verticalAlign": "middle"
                      }),
            dcc.Input(id='weight', placeholder='weight', type='number', value=1, style={
                          "height": "36px",
                          "padding": "6px 10px",
                          "border": "1px solid #ccc",
                          "borderRadius": "6px",
                          "boxSizing": "border-box",
                          "lineHeight": "normal",
                          "fontSize": "14px",
                          "display": "inline-block",
                          "verticalAlign": "middle"
                      }),
            dcc.Dropdown(
                id="duplex",
                options=[
                    {"label": "Повний", "value": 1},
                    {"label": "Напівдуплекс", "value": 0},
                ],
                value=network.TCP,
                clearable=False,
                style={
                    "height": "36px",
                    "lineHeight": "36px",
                    "minWidth": "100px",
                    "borderRadius": "6px",
                    "fontSize": "14px",
                    "display": "inline-block",
                    "verticalAlign": "middle"
                },
            ),
            html.Button(
                'Додати з\'єднання',
                id='add_connection',
                style=self.button_style
            ),
        ], style={
            'display': 'flex',
            'flexDirection': 'row',
            'alignItems': 'center',
            'margin': '10px 0',
            'gap': '10px',
        }),

        # Панель управления сетью
        html.Div([
            html.Button(
                'Додати маршрутизатор',
                id='add_router',
                style=self.button_style
            ),
            html.Button(
                'Згенерувати мережу',
                id='generate_network',
                style=self.button_style
            )
        ], style={
            'display': 'flex',
            'flexDirection': 'row',
            'gap': '10px',
            'marginTop': '10px'
        })
    ])

