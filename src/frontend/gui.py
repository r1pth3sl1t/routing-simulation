from dash import Dash, html, dcc, Output, Input, State, no_update
import dash_cytoscape as cyto
from pandas.tseries.holiday import next_workday

from src.core.network import Network


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
            Output('graph', 'elements', allow_duplicate=True),
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
            if not any(r.id == int(node) for r in self.network.routers):
                return elements, html.Span(str(self.network.get_avg_network_power()), id="network_power")
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
        return html.Div(
            [
                html.P("Ідентифікатор: %s" % data.get('label')),
                html.Div(
                    router.routing_table.to_html(),
                    style={
                        "maxHeight": "300px",
                        "overflowY": "auto",
                        "border": "1px solid #ccc"
                    }
                ),
                dcc.Input(id='dst_router', placeholder='target'),
                html.Button('Знайти найкоротший шлях до', id='find_shortest', n_clicks=0),
                html.Button('Заповнити таблицю маршрутизації', id='fillup_routing_table', n_clicks=0),
                html.Button('Видалити маршрутизатор', id='remove_router', n_clicks=0),
            ]
        )

    def find_shortest(self, n, router, dst_router):
        if not n:
            return no_update
        print("dest %s" % dst_router)
        path = self.network.find_shortest(int(router['data'].get('id')), int(dst_router))
        styles = []
        for p in path:
            styles.append({
                'selector': f'edge[source = "{p}"][target = "{path[p]}"], edge[source = "{path[p]}"][target = "{p}"]',
                'style': {'line-color': 'green', 'width': 4}
            })
        print(path)
        return self.base_graph_stylesheet + styles

    def display_connection_info(self, tap_connection):
        if tap_connection is None:
            return no_update
        data = tap_connection['data']
        connection = next((c for c in self.network.get_router_by_id(int(data.get('source'))).connections
                           if c.equals(int(data.get('source')), int(data.get('target')))), None)
        return html.Div(
            [
                html.P("Вага: %s" % connection.weight),
                html.P("Дуплекс: %s" % ("Повний" if connection.duplex else "Напівдуплекс")),
                html.Button('Видалити з\'єднання', id='remove_connection', n_clicks=0),
             ]
        )

    def generate_network(self, n, elements):
        if not n:
            return elements

        self.network.generate()
        return self.refresh_graph()

    def refresh_graph(self):
        elements = []
        for router in self.network.routers:
            elements.append({'data': {'id': str(router.id), 'label': str(router.id)}})
            for connection in router.connections:
                if connection.r1.id == router.id:
                    elements.append({'data': {'source': str(router.id), 'target': str(connection.r2.id),
                                              'weight': connection.weight, 'duplex': connection.duplex}})

        return elements

    def refresh_network_power(self):
        return html.Span(str(self.network.get_avg_network_power()), id="network_power")

    def refresh_page(self):
        elements = []
        for router in self.network.routers:
            elements.append({'data': {'id': str(router.id), 'label': str(router.id)}})
            for connection in router.connections:
                if connection.r1.id == router.id:
                    elements.append({'data': {'source': str(router.id), 'target': str(connection.r2.id), 'weight': connection.weight, 'duplex': connection.duplex}})

        return html.Div([
                html.Div([
                    cyto.Cytoscape(id='graph', layout={'name': 'cose', 'idealEdgeLength': 5, 'nodeRepulsion': 4000, 'animate': True},
                                   style={'width': '70%', 'height': '600px', 'border': '1px solid #ccc'},
                                   elements=elements,
                                   stylesheet=self.base_graph_stylesheet,
                    ),
                    html.Div([
                        html.Div(
                            id='node-info',
                            children="Натисніть на елемент, щоб отримати інформацію",
                        ),
                        html.Footer([
                            html.Span("Степінь мережі:"),
                            self.refresh_network_power()
                        ], style={"position": "fixed", "bottom": "0"})
                    ])
                ], style={
                    'display': 'flex',
                    'flexDirection': 'row',
                    'height': '600px'
                }),
            html.Div([
                dcc.Input(id='src', placeholder='source'),
                dcc.Input(id='dst', placeholder='target'),
                dcc.Input(id='weight', placeholder='weight', type='number', value=1),
                dcc.Dropdown(
                    id='duplex',
                    options=[
                        {'label': 'half', 'value': 0},
                        {'label': 'full', 'value': 1}
                    ],
                    placeholder='duplex',
                    value=0,
                    clearable=False,
                ),
                html.Button('Додати з\'єднання', id='add_connection'),
            ], style={
                'display': 'flex',
                'flexDirection': 'row',
                'alignItems': 'center',
                'margin': '10px',
                'gap': '10px',
            }),
            html.Div([
                html.Button('Додати маршрутизатор', id='add_router'),
                html.Button('Згенерувати мережу', id='generate_network')
            ]),
        ])

