from typing import List
import networkx as nx
# from torch_geometric.data import Data


def create_networkx_graph(nodes: List[dict], edges: List[dict], name: str = None) -> nx.DiGraph:
    """
    Generate a networkx graph from lists of nodes and edges.

    :param nodes: The list of nodes returned from a HeliumArangoHTTPClient graph request.
    :param edges: The list of edges returned from a HeliumArangoHTTPClient graph request.
    :param name: (optional) The name of graph.
    :return: The networkx directed graph (nx.DiGraph) with full node/edge attributes.
    """
    g = nx.DiGraph(name=name)
    node_attrs, edge_attrs = {}, {}
    for node in nodes:
        g.add_node(node['address'])
        node_attrs[node['address']] = node

    for edge in edges:
        g.add_edge(edge['_from'], edge['_to'])
        edge_attrs[(edge['_from'], edge['_to'])] = edge

    nx.set_node_attributes(g, node_attrs)
    nx.set_edge_attributes(g, edge_attrs)

    return g


def convert_nx_to_torch_geometric(g: nx.DiGraph, group_node_attrs: List[str], group_edge_attrs: List[str]):
    """
    Convert a networkx graph to a torch-geometric Data instance.
    :param g: The networkx.DiGraph instance.
    :param group_node_attrs: (optional) The node attributes to be concatenated and added to data.x. (default: None)
    :param group_edge_attrs: (optional) The edge attributes to be concatenated and added to data.edge_attr. (default: None)
    :return: The torch_geometric.data.Data instance.
    """
    from torch_geometric.utils import from_networkx

    # torch does not like non-numeric types in their Data objects.
    for node in g.nodes():
        for k, v in g.nodes[node].items():
            if type(v) not in [float, int]:
                g.nodes[node][k] = 0
    data = from_networkx(g, group_node_attrs, group_edge_attrs)

    return data

