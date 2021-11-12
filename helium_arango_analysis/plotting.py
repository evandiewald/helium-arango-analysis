from networkx.drawing.layout import spring_layout, spiral_layout, kamada_kawai_layout
import networkx as nx
import plotly.graph_objects as go
import numpy as np
from pyvis.network import Network


def set_new_attr_from_existing(g: nx.DiGraph, in_attr: str, out_attr: str, attr_type: str) -> nx.DiGraph:
    """
    Utility for creating new attributes from existing in graph. Useful for setting keywords for visualization/analysis, e.g. size, pos, weight.
    :param g: The incoming graph.
    :param in_attr: The attribute to copy values from for each entity.
    :param out_attr: The name of the new attribute.
    :param attr_type: One of {'nodes', 'edges'}
    :return: The updated graph.
    """
    valid_attr_types = {'nodes', 'edges'}
    if attr_type not in valid_attr_types:
        raise ValueError(f'attr_type argument must be one of {valid_attr_types}')
    if attr_type == 'nodes':
        node_attrs = {}
        for node in g.nodes(data=True):
            node_attrs[node[0]] = {out_attr: node[1][in_attr]}
        nx.set_node_attributes(g, node_attrs)
    if attr_type == 'edges':
        edge_attrs = {}
        for edge in g.edges(data=True):
            edge_attrs[edge[0]] = {out_attr: edge[1][in_attr]}
        nx.set_edge_attributes(g, edge_attrs)
    return g


def plot_graph_simple(g: nx.DiGraph):
    net = Network()
    net.from_nx(g)
    net.show('example.html')


def plot_witness_graph_plotly(G: nx.DiGraph):
    edge_x = []
    edge_y = []
    for edge in G.edges():
        x0, y0 = G.nodes[edge[0]]['coordinates']
        x1, y1 = G.nodes[edge[1]]['coordinates']
        edge_x.append(x0)
        edge_x.append(x1)
        edge_x.append(None)
        edge_y.append(y0)
        edge_y.append(y1)
        edge_y.append(None)

    edge_trace = go.Scatter(
        x=edge_x, y=edge_y,
        line=dict(width=0.5, color='#888'),
        hoverinfo='none',
        mode='lines')

    node_x = []
    node_y = []
    node_text = []
    for node in G.nodes():
        x, y = G.nodes[node]['coordinates']
        node_text.append(G.nodes[node]['name'])
        node_x.append(x)
        node_y.append(y)

    node_trace = go.Scatter(
        x=node_x, y=node_y,
        mode='markers',
        hoverinfo='text',
        marker=dict(
            showscale=True,
            # colorscale options
            # 'Greys' | 'YlGnBu' | 'Greens' | 'YlOrRd' | 'Bluered' | 'RdBu' |
            # 'Reds' | 'Blues' | 'Picnic' | 'Rainbow' | 'Portland' | 'Jet' |
            # 'Hot' | 'Blackbody' | 'Earth' | 'Electric' | 'Viridis' |
            colorscale='YlGnBu',
            reversescale=True,
            color=[],
            size=10,
            colorbar=dict(
                thickness=15,
                title='Node Connections',
                xanchor='left',
                titleside='right'
            ),
            line_width=2))

    node_adjacencies = []
    for node, adjacencies in enumerate(G.adjacency()):
        node_adjacencies.append(len(adjacencies[1]))


    node_trace.marker.color = node_adjacencies
    node_trace.text = node_text

    fig = go.Figure(data=[edge_trace, node_trace],
                    layout=go.Layout(
                        title='<br>Hotspot Witness Graph',
                        titlefont_size=16,
                        showlegend=False,
                        hovermode='closest',
                        margin=dict(b=20, l=5, r=5, t=40),
                        xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                        yaxis=dict(showgrid=False, zeroline=False, showticklabels=False))
                    )
    fig.show()


def _get_token_flow_traces(G: nx.DiGraph):
    positions = spring_layout(G)
    edge_x = []
    edge_y = []
    for edge in G.edges():
        x0, y0 = positions[edge[0]]
        x1, y1 = positions[edge[1]]
        edge_x.append(x0)
        edge_x.append(x1)
        edge_x.append(None)
        edge_y.append(y0)
        edge_y.append(y1)
        edge_y.append(None)

    edge_trace = go.Scatter(
        x=edge_x, y=edge_y,
        line=dict(width=0.5, color='#888'),
        hoverinfo='none',
        mode='lines')

    node_x = []
    node_y = []
    node_text = []
    node_balances = []
    for node in G.nodes():
        node_text.append(G.nodes[node]['address'])
        node_balances.append(np.log10(G.nodes[node]['balance']))
        x, y = positions[node]
        node_x.append(x)
        node_y.append(y)

    node_trace = go.Scatter(
        x=node_x, y=node_y,
        mode='markers',
        hoverinfo='text',
        marker=dict(
            showscale=True,
            colorscale='YlGnBu',
            reversescale=True,
            color=[],
            size=10,
            colorbar=dict(
                thickness=15,
                title='Log(Account Balance)',
                xanchor='left',
                titleside='right'
            ),
            line_width=2))
    return node_trace, edge_trace, node_text, node_balances


def plot_payee_graph(G: nx.DiGraph, sized_by: str = 'total_received'):
    node_trace, edge_trace, node_text, node_balances = _get_token_flow_traces(G)
    total_received, num_payments = [], []
    for node, adjacencies in enumerate(G.in_edges(data=True)):
        total_received_by_node, num_payments_to_node = 0, 0
        total_received_by_node += adjacencies[2]['total_amount'] / 1e12
        num_payments_to_node += adjacencies[2]['num_payments']
        total_received.append(total_received_by_node)
        num_payments.append(num_payments_to_node)

    if sized_by == 'total_received':
        node_trace.marker.size = total_received
        title = '<br>Token Flow: Nodes Sized by Total Amount Received over Time Period'
    elif sized_by == 'num_payments':
        node_trace.marker.size = num_payments
        title = '<br>Token Flow: Nodes Sized by Total Number of Payments Received over Time Period'
    node_trace.text = node_text
    node_trace.marker.color = node_balances

    fig = go.Figure(data=[edge_trace, node_trace],
                    layout=go.Layout(
                        title=title,
                        titlefont_size=16,
                        showlegend=False,
                        hovermode='closest',
                        margin=dict(b=20, l=5, r=5, t=40),
                        xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                        yaxis=dict(showgrid=False, zeroline=False, showticklabels=False))
                    )
    fig.show()


def plot_payer_graph(G: nx.DiGraph, sized_by: str = 'total_paid'):
    node_trace, edge_trace, node_text, node_balances = _get_token_flow_traces(G)
    total_received, num_payments = [], []
    for node, adjacencies in enumerate(G.adjacency()):
        total_paid_by_node, num_payments_from_node = 0, 0
        for payee in adjacencies[1]:
            payment = adjacencies[1][payee]
            total_paid_by_node += payment['total_amount'] / 1e12
            num_payments_from_node += payment['num_payments']
        total_received.append(total_paid_by_node)
        num_payments.append(num_payments_from_node)

    if sized_by == 'total_paid':
        node_trace.marker.size = total_received
        title = '<br>Token Flow: Nodes Sized by Total Amount Paid over Time Period'
    elif sized_by == 'num_payments':
        node_trace.marker.size = num_payments
        title = '<br>Token Flow: Nodes Sized by Total Number of Payments Sent over Time Period'
    node_trace.text = node_text
    node_trace.marker.color = node_balances

    fig = go.Figure(data=[edge_trace, node_trace],
                    layout=go.Layout(
                        title=title,
                        titlefont_size=16,
                        showlegend=False,
                        hovermode='closest',
                        margin=dict(b=20, l=5, r=5, t=40),
                        xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                        yaxis=dict(showgrid=False, zeroline=False, showticklabels=False))
                    )
    fig.show()
