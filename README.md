# helium-arango-analysis
Tools for querying, visualizing, and modeling network graphs on the [Helium](https://docs.helium.com/) blockchain.

## About
Helium's Blockchain API is an effective way to view historical data stored on-chain, but the ledger-based format is less useful for feeding directly into network models. In this project, we propose to build a framework for a graph-based representation of blockchain activity, including Proof of Coverage and Token Flow. By capturing the natural adjacency between hotspots and accounts, we will be able to build machine learning models to, for instance, identify likely "gaming" behavior and predict coverage maps based on hotspot placement. 

[More details in the full project proposal](https://github.com/dewi-alliance/grants/issues/23).

## Dependencies
To run use these tools, you will need a running instance of [`helium-arango-http`](https://github.com/evandiewald/helium-arango-http), a REST API that serves queries of an ArangoDB database.

## Quick setup
Clone the repository and initialize a virtual environment with [`requirements.txt`](requirements.txt), e.g. 

```pip install -r requirements.txt```

**Note:** By default, the CPU-only version of [PyTorch 1.10](https://pytorch.org/docs/stable/index.html) is installed. If you want to use a CUDA-compatible GPU to train graph neural networks, make sure to adjust accordingly.

## Usage

The [`helium_arango_analysis.client.HeliumArangoHTTPClient`](https://github.com/evandiewald/helium-arango-analysis/blob/295ea319e4f54dcb60f1b712c4a7a83da32257e7/helium_arango_analysis/client.py#L7) base class is a [requests](https://docs.python-requests.org/en/latest/) based wrapper for the routes provided by the HTTP API. Initialize the client by providing the URL to the endpoint, e.g. 

```python
from helium_arango_analysis.client import HeliumArangoHTTPClient as Client

client = Client('http://localhost:8000/')
```

### Getting Graphs

Because the ArangoDB instance natively stores blockchain data as nodes and edges, the API focuses on queries that address *adjacencies* in the Helium Network, such as those between accounts (token flow) and hotspots (witness receipts). With this representation, we can leverage graph-based analyses to extract insights about network activity.

**Get Witness Graph in H3 Hex**
```python
import h3
hex = h3.h3_to_parent('882a847063fffff', 5)
nodes, edges = client.get_witness_graph_in_hex(hex=hex).values()

# nodes are hotspots
print(nodes[0])
# {'address': '13A7h7obhgFgey8rpZJm6PCnp2EumsG6YX1fKDhGhSmkeKLudgj',
#   'dc_balance': 0,
#   'dc_nonce': 0,
#   'security_balance': 0,
#   'balance': 14868400000000,
#   'nonce': 18,
#   'first_block': 133374,
#   'last_block': 216368,
#   'staked_balance': 0,
#   '_id': 'accounts/13A7h7obhgFgey8rpZJm6PCnp2EumsG6YX1fKDhGhSmkeKLudgj',
#   '_key': '13A7h7obhgFgey8rpZJm6PCnp2EumsG6YX1fKDhGhSmkeKLudgj',
#   '_rev': '_dO9xW02--S'}

# edges are witness receipts with distances
print(edges[0])
# {'_from': '112nUEtrKPrgWtczpbira7aDU5271qduDfJm8Y2WSXjWwpkAHdgJ',
#  '_to': '11rraissynzdXzuvR9C9zsiPuZCMsJ33jMszpNqafKhCN8T1LtJ',
#  'snr': 0,
#  'rssi': -108,
#  'distance_m': 4332.713990650966}
```

**Token Flow Graph to Top Payees**

```python
# get token flow graph from top token recipients over a week
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
```

### Adapters (NetworkX and torch-geometric)

**NetworkX**

[NetworkX](https://networkx.org/) provides a wide range of algorithms, layouts, and visualization tools to help model graphs. We provide an adapter to construct NetworkX graphs from the HTTP responses. From there, you can directly extract metrics such as Pagerank and Betweenness Centrality. 

```python
# convert a graph to networkx Directed Graph
from networkx import is_directed, betweenness_centrality
from helium_arango_analysis.adapters import create_networkx_graph

witness_graph = create_networkx_graph(nodes, edges, name='Witnesses in Pittsburgh')
print(is_directed(witness_graph))
# True

bc = betweenness_centrality(witness_graph)
print(bc)
# {'112nUEtrKPrgWtczpbira7aDU5271qduDfJm8Y2WSXjWwpkAHdgJ': 0.012254901960784312,
#  '112AVskHifCVhotTAzS167r9yei9qfiYSBCSBm33TtoxpfRMsLwa': 0.13112745098039214,
#  '112NWnxeXBSrFmQgpCDKYvkoGTtTsyD2uy6xDV1yEyT21vQ7C9qD': 0.1256127450980392,
```

**torch-geometric**

[torch-geometric]() is a popular library for deep learning on geometric datasets. Use the [`convert_nx_to_torch_geometric`] adapter to convert graphs into [`torch_geometric.data.Data`](https://pytorch-geometric.readthedocs.io/en/latest/modules/data.html#torch_geometric.data.Data) objects that can be used to train and evaluate graph neural networks. 

```python
from helium_arango_analysis.adapters import convert_nx_to_torch_geometric

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
```

### Visualization

Visualization is a work in progress, as I am playing with a few different libraries to try to figure out the best way to plot the graphs. NetworkX provides basic, matplotlib-esque functionality with [`nx.draw(G)`](https://networkx.org/documentation/stable/reference/drawing.html?highlight=draw), and the [`plotting`](helium_arango_analysis/plotting.py) submodule defines some experimental functions using [plotly](https://plotly.com/python/) and [pyvis](https://pyvis.readthedocs.io/en/latest/). 

```python
from helium_arango_analysis.plotting import plot_witness_graph_plotly, plot_graph_simple

plot_witness_graph_plotly(witness_graph) # opens interactive plotly graph in your browser

plot_graph_simple(witness_graph) # pyvis
```

More usage examples in [`examples.py`](examples.py).

## Related Work

- [`Exploring the Helium Network with Graph Theory`](https://towardsdatascience.com/exploring-the-helium-network-with-graph-theory-66cbb8bffff9): Blog post inspiring much of this work.
- [`evandiewald/helium-arango-etl`](https://github.com/evandiewald/helium-arango-etl): ETL service that converts relational blockchain data into a native graph format for storage in [ArangoDB](https://www.arangodb.com/).
- [`evandiewald/helium-arango-http`](https://github.com/evandiewald/helium-arango-http): an HTTP API to run queries on the data stored in the ArangoDB database populated by the ETL.

## Acknowledgements
This project is supported by a grant from the [Decentralized Wireless Alliance](https://dewi.org).

