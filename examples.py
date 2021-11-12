import networkx as nx

from helium_arango_analysis.client import HeliumArangoHTTPClient as Client
from helium_arango_analysis.adapters import create_networkx_graph, convert_nx_to_torch_geometric
from helium_arango_analysis.plotting import plot_witness_graph_plotly, plot_payee_graph, plot_payer_graph, plot_graph_simple
from networkx import betweenness_centrality
import h3


client = Client('http://localhost:8000')

hex = h3.h3_to_parent('882a847063fffff', 5)
nodes, edges = client.get_witness_graph_in_hex(hex=hex).values()
for node in nodes:
    node['witnesses'] = []
witness_graph = create_networkx_graph(nodes, edges, name='witnesses')
tg_witness_graph = convert_nx_to_torch_geometric(witness_graph,
                                                 group_node_attrs=['elevation', 'gain'],
                                                 group_edge_attrs=['snr', 'rssi', ])
print(tg_witness_graph.num_features)
# plot_witness_graph_plotly(witness_graph)

nodes, edges = client.get_top_payees_graph(limit=50).values()
payee_graph = create_networkx_graph(nodes, edges, 'accounts')

# plot_graph_simple(payee_graph)
# plot_payee_graph(payee_graph)





# nodes, edges = client.get_top_payers_graph(limit=50).values()
# payer_graph = create_networkx_graph(nodes, edges, 'accounts')
# plot_payee_graph(payer_graph)
#
# bc = betweenness_centrality(witness_graph, weight='distance_m')