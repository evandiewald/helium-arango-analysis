from helium_arango_analysis.adapters import create_networkx_graph
from spektral.data import Graph
import numpy as np
import networkx as nx


def make_spektral_graph(nodes: list, edges: list, node_features: list, edge_features: list, output=None) -> Graph:
    """
    Creates a spektral graph object for assembling training datasets.

    :param nodes: The list of nodes.
    :param edges: The list of edges.
    :param node_features: A list of node feature keys, e.g. ['elevation', 'gain']
    :param edge_features: A list of edge feature keys, e.g. ['rssi', 'snr']
    :param output: An optional string key to define the target of the node-based regression task, e.g. 'reward_scale'
    :return: The spektral.data.graph.Graph object
    """
    n_nodes, n_edges, n_node_features, n_edge_features = len(nodes), len(edges), len(node_features), len(edge_features)

    g = create_networkx_graph(nodes, edges)
    a = nx.convert_matrix.to_scipy_sparse_matrix(g)
    x = np.empty((n_nodes, n_node_features))

    if output:
        y = np.empty((n_nodes,1))
    else:
        y = None
    nodelist, edgelist = list(g.nodes), list(g.edges)
    for i in range(len(nodelist)):
        node_data = g.nodes(data=True)[nodelist[i]]
        try:
            y[i] = node_data[output]
        except TypeError:
            pass
        for j in range(n_node_features):
            x[i,j] = node_data[node_features[j]]
    if edge_features:
        e = np.empty((n_edges, n_edge_features))
        for i in range(n_edges):
            edge_data = g.edges[edgelist[i][0], edgelist[i][1]]
            for j in range(n_edge_features):
                e[i,j] = edge_data[edge_features[j]]
    else:
        e = None

    y = np.nan_to_num(y, nan=0)
    return Graph(x, a, e, y)