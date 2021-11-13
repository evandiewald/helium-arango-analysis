from helium_arango_analysis.client import HeliumArangoHTTPClient as Client
from helium_arango_analysis.adapters import create_networkx_graph, convert_nx_to_torch_geometric
from helium_arango_analysis.plotting import plot_witness_graph_plotly, plot_payee_graph, plot_payer_graph, plot_graph_simple


## initialize the HTTP client by providing the URL to the server
client = Client('http://localhost:8000')

## get recent witness receipts (useful for checking, e.g. rssi vs. distance for a datarate
receipts = client.get_sample_of_recent_witness_receipts(limit=1000)
print(receipts['receipts'][0])
# {'_key': '6b3c3dffe6f61cc812df48bccf3c9b02',
#  '_id': 'witnesses/6b3c3dffe6f61cc812df48bccf3c9b02',
#  '_from': 'hotspots/112RP2Y33KKv6f2EJm5VUCaYuG8mshbNtFtxiZ7ScwQWABS9562j',
#  '_to': 'hotspots/112VVqgL1LRxy6jhAM4AtNVa4qDcw1KmfGf4HjkjQAszo23EqYYY',
#  '_rev': '_dO9s9VO--H',
#  'time': 1582396185,
#  'snr': 0,
#  'owner': '14gaNAfNSL8pPAVjTyy8LhRjVgw9t8JunooEmCSyXLAX9A3pfMF',
#  'signal': -120,
#  'channel': 0,
#  'gateway': '112VVqgL1LRxy6jhAM4AtNVa4qDcw1KmfGf4HjkjQAszo23EqYYY',
#  'datarate': None,
#  'location': '8c2a340824267ff',
#  'frequency': 0,
#  'timestamp': 1582395607524872246,
#  'packet_hash': 'MV2gwnYnrl_Gu8oPeia-UzZGq-hBWPVM0l_uE88b-vU'}

## get hotspot witness graph in hex
import h3
hex = h3.h3_to_parent('882a847063fffff', 5)
nodes, edges = client.get_witness_graph_in_hex(hex=hex).values()

# nodes are hotspots
print(nodes[0])
# {'_key': '112nUEtrKPrgWtczpbira7aDU5271qduDfJm8Y2WSXjWwpkAHdgJ',
#  '_id': 'hotspots/112nUEtrKPrgWtczpbira7aDU5271qduDfJm8Y2WSXjWwpkAHdgJ',
#  '_rev': '_dO9xXdG--T',
#  'address': '112nUEtrKPrgWtczpbira7aDU5271qduDfJm8Y2WSXjWwpkAHdgJ',
#  'owner': '14FUSqWYcWfQd7KQjrDSPXehsxvtJqxFf2q2QdxakbH4597KCz9',
#  'location': '8c2a847004b05ff',
#  'last_poc_challenge': 217323,
#  'last_poc_onion_key_hash': 'ZHXuud7wao-NWT7_66JHx9G5vyHxQgLjlST8Y7uteqQ',
#  'witnesses': {},
#  'first_block': 134960,
#  'last_block': 217359,
#  'nonce': 3,
#  'name': 'big-maroon-ant',
#  'first_timestamp': '2019-12-13 22:42:18+00:00',
#  'reward_scale': None,
#  'elevation': 0,
#  'gain': 12,
#  'location_hex': '882a847005fffff',
#  'mode': 'GatewayMode.full',
#  'payer': '14fzfjFcHpDR1rTH8BNPvSi5dKBbgxaDnmsVPbCjuq9ENjpZbxh',
#  'status': 'online',
#  'geo_location': {'coordinates': [-79.93777048403096, 40.411233460016334],
#   'type': 'Point'}}

# edges are witness receipts with distances
print(edges[0])
# {'_from': '112nUEtrKPrgWtczpbira7aDU5271qduDfJm8Y2WSXjWwpkAHdgJ',
#  '_to': '11rraissynzdXzuvR9C9zsiPuZCMsJ33jMszpNqafKhCN8T1LtJ',
#  'snr': 0,
#  'rssi': -108,
#  'distance_m': 4332.713990650966}

# convert a graph to networkx Directed Graph
from networkx import is_directed
witness_graph = create_networkx_graph(nodes, edges, name='Witnesses in Pittsburgh')
print(is_directed(witness_graph))
# True

# run networkx analyses
from networkx import betweenness_centrality
bc = betweenness_centrality(witness_graph)
print(bc)
# {'112nUEtrKPrgWtczpbira7aDU5271qduDfJm8Y2WSXjWwpkAHdgJ': 0.012254901960784312,
#  '112AVskHifCVhotTAzS167r9yei9qfiYSBCSBm33TtoxpfRMsLwa': 0.13112745098039214,
#  '112NWnxeXBSrFmQgpCDKYvkoGTtTsyD2uy6xDV1yEyT21vQ7C9qD': 0.1256127450980392,

# convert to torch-geometric for graph neural networks
tg_witness_graph = convert_nx_to_torch_geometric(witness_graph,
                                                 group_node_attrs=['elevation', 'gain'],
                                                 group_edge_attrs=['snr', 'rssi', ])
print(f'Num nodes: {tg_witness_graph.num_nodes}\n'
      f'Num edges: {tg_witness_graph.num_edges}\n'
      f'Num node features: {tg_witness_graph.num_node_features}\n'
      f'Num edge features: {tg_witness_graph.num_edges}')
# Num nodes: 18
# Num edges: 42
# Num node features: 2
# Num edge features: 42

# some plotting (work in progress)
plot_witness_graph_plotly(witness_graph) # opens interactive plotly graph in your browser

# get token flow graph from top token recipients over last week
now_ts = 1582396185
week_ago_ts = now_ts - 3600*24*7
nodes, edges = client.get_top_payees_graph(limit=50, min_time=week_ago_ts, max_time=now_ts).values()

# nodes are accounts
print(nodes[0])
# {'address': '13ucSyoF1gDE2PYuHdCuxRFDy8RbnGSoqaS7RqBNe5U5KgLjNk3',
#  'dc_balance': 0,
#  'dc_nonce': 0,
#  'security_balance': 0,
#  'balance': 55300000000000,
#  'nonce': 0,
#  'first_block': 140062,
#  'last_block': 212402,
#  'staked_balance': 0,
#  '_id': 'accounts/13ucSyoF1gDE2PYuHdCuxRFDy8RbnGSoqaS7RqBNe5U5KgLjNk3',
#  '_key': '13ucSyoF1gDE2PYuHdCuxRFDy8RbnGSoqaS7RqBNe5U5KgLjNk3',
#  '_rev': '_dO9xW0W--J'}

# edges are payments
print(edges[0])
# {'_to': '13A7h7obhgFgey8rpZJm6PCnp2EumsG6YX1fKDhGhSmkeKLudgj',
#   '_from': '14Kr1J64L2BZHRc2Ncvginn5BvrAmnUYuoFwf7Ywe6WnTLtPugM',
#   'total_amount': 61920100000000.0,
#   'num_payments': 70}

payee_graph = create_networkx_graph(nodes, edges, 'accounts')
plot_payee_graph(payee_graph) # opens interactive plotly graph in your browser

