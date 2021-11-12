import requests
from typing import Optional, List
from datetime import datetime
import networkx as nx


class HeliumArangoHTTPClient(object):
    def __init__(self, base_url: str):
        """
        Initialize a Helium Arango HTTP Client.

        :param base_url: The base url for the helium-arango-http server, e.g. http://localhost:8000/
        """
        if base_url[-1] == '/':
            base_url = base_url[:-1]
        self.base_url = base_url

    @staticmethod
    def get_request(url: str, params: dict=None):
        response = requests.get(url, params=params)
        if response.status_code != 200:
            raise Exception('Request failed. Please check your query parameters and make sure that the HTTP API is online.')
        else:
            return response.json()

    def get_payments_from_account(self, address: str, limit: Optional[int] = 100, min_time: Optional[int] = 0, max_time: Optional[int] = int(datetime.utcnow().timestamp())) -> List[dict]:
        """
        Get payments from an account, grouped by payee and sorted by amount. Also includes payment counts for each.

        :param address: The HNT wallet address of the payer.
        :param limit: The max number of payees to return.
        :param min_time: The minimum UTC timestamp to consider.
        :param max_time: The maximum UTC timestamp to consider.
        :return:
        """
        params = {
            'limit': limit,
            'min_time': min_time,
            'max_time': max_time
        }
        url = self.base_url + f'/payments/{address}/from'
        return self.get_request(url, params=params)

    def get_payments_to_account(self, address: str, limit: Optional[int] = 100, min_time: Optional[int] = 0, max_time: Optional[int] = int(datetime.utcnow().timestamp())) -> List[dict]:
        """
        Get payments to an account, grouped by payer and sorted by amount. Also includes payment counts for each.

        :param address: The HNT wallet address of the payee.
        :param limit: The max number of payers to return.
        :param min_time: The minimum UTC timestamp to consider.
        :param max_time: The maximum UTC timestamp to consider.
        :return:
        """
        params = {
            'limit': limit,
            'min_time': min_time,
            'max_time': max_time
        }
        url = self.base_url + f'/payments/{address}/to'
        return self.get_request(url, params=params)

    def get_top_payment_totals(self, limit: Optional[int] = 100, min_time: Optional[int] = 0, max_time: Optional[int] = int(datetime.utcnow().timestamp())) -> List[dict]:
        """
        Get top payments (payer, payee) pair, sorted by total HNT paid.

        :param limit: The max number of payment pairs to return.
        :param min_time: The minimum UTC timestamp to consider.
        :param max_time: The maximum UTC timestamp to consider.
        :return:
        """
        params = {
            'limit': limit,
            'min_time': min_time,
            'max_time': max_time
        }
        url = self.base_url + f'/payments/totals'
        return self.get_request(url, params=params)

    def get_top_payment_counts(self, limit: Optional[int] = 100, min_time: Optional[int] = 0, max_time: Optional[int] = int(datetime.utcnow().timestamp())) -> List[dict]:
        """
        Get top payments (payer, payee) pair, sorted by number of payments.

        :param limit: The max number of payment pairs to return.
        :param min_time: The minimum UTC timestamp to consider.
        :param max_time: The maximum UTC timestamp to consider.
        :return:
        """
        params = {
            'limit': limit,
            'min_time': min_time,
            'max_time': max_time
        }
        url = self.base_url + f'/payments/counts'
        return self.get_request(url, params=params)

    def get_top_payers(self, limit: Optional[int] = 100, min_time: Optional[int] = 0,
                               max_time: Optional[int] = int(datetime.utcnow().timestamp())) -> List[dict]:
        """
        Get top payers, sorted by amount paid. Also includes payment counts for each.

        :param limit: The max number of payers to return.
        :param min_time: The minimum UTC timestamp to consider.
        :param max_time: The maximum UTC timestamp to consider.
        :return:
        """
        params = {
            'limit': limit,
            'min_time': min_time,
            'max_time': max_time
        }
        url = self.base_url + f'/payments/payers'
        return self.get_request(url, params=params)

    def get_top_payees(self, limit: Optional[int] = 100, min_time: Optional[int] = 0,
                               max_time: Optional[int] = int(datetime.utcnow().timestamp())) -> List[dict]:
        """
        Get top payees, sorted by amount received. Also includes payment counts for each.

        :param limit: The max number of payees to return.
        :param min_time: The minimum UTC timestamp to consider.
        :param max_time: The maximum UTC timestamp to consider.
        :return:
        """
        params = {
            'limit': limit,
            'min_time': min_time,
            'max_time': max_time
        }
        url = self.base_url + f'/payments/payees'
        return self.get_request(url, params=params)

    def get_top_payers_graph(self, limit: Optional[int] = 100, min_time: Optional[int] = 0,
                               max_time: Optional[int] = int(datetime.utcnow().timestamp())) -> dict:
        """
        Starting with the top payers, generate the graph of token flow from these accounts.

        :param limit: The max number of top payers to seed the graph.
        :param min_time: The minimum UTC timestamp to consider.
        :param max_time: The maximum UTC timestamp to consider.
        :return:
        """
        params = {
            'limit': limit,
            'min_time': min_time,
            'max_time': max_time
        }
        url = self.base_url + f'/payments/payers/graph'
        return self.get_request(url, params=params)

    def get_top_payees_graph(self, limit: Optional[int] = 100, min_time: Optional[int] = 0,
                               max_time: Optional[int] = int(datetime.utcnow().timestamp())) -> dict:
        """
        Starting with the top payees, generate the graph of token flow to these accounts.

        :param limit: The max number of top payees to seed the graph.
        :param min_time: The minimum UTC timestamp to consider.
        :param max_time: The maximum UTC timestamp to consider.
        :return:
        """
        params = {
            'limit': limit,
            'min_time': min_time,
            'max_time': max_time
        }
        url = self.base_url + f'/payments/payees/graph'
        return self.get_request(url, params=params)

    def get_witness_graph_near_coords(self, lat: float, lon: float, limit: Optional[int] = 100) -> dict:
        """
        Starting with the closest hotspots to a given coordinate, generate the recent witness graph, including signal details.

        :param lat: The latitude of the query coordinate.
        :param lon: The longitude of the query coordinate.
        :param limit: The max number of nearby hotspots to seed the graph. Note that the nodes list will also include any witnesses.
        :return:
        """
        params = {
            'limit': limit,
            'lat': lat,
            'lon': lon
        }
        url = self.base_url + f'/hotspots/coords/graph'
        return self.get_request(url, params=params)

    def get_witness_graph_in_hex(self, hex: str) -> dict:
        """
        Generate the witness graph within a hex. Be careful not to choose an excessively large hex when querying over an HTTP API.

        :param hex: An h3 hex to consider.
        :return:
        """
        params = {
            'hex': hex
        }
        url = self.base_url + f'/hotspots/hex/graph'
        return self.get_request(url, params=params)

    def get_outbound_witnesses_for_hotspot(self, address: str) -> List[dict]:
        """
        Get the list of hotspots that have recently witnessed a challenge from this hotspot.

        :param address: The hotspot address.
        :return:
        """
        url = self.base_url + f'/hotspots/{address}/outbound'
        return self.get_request(url)

    def get_inbound_witnesses_for_hotspot(self, address: str) -> List[dict]:
        """
        Get the list of hotspots that this hotspot has recently witnessed.

        :param address: The hotspot address.
        :return:
        """
        url = self.base_url + f'/hotspots/{address}/inbound'
        return self.get_request(url)

    def get_sample_of_recent_witness_receipts(self, address: Optional[str] = None, limit: Optional[int] = None):
        """
        Get sample of recent witness receipts. If no address is specified, will return receipts from the network overall.

        :param address: (optional) A hotspot address to focus on.
        :param limit: (optional) The maximum number of receipts to return.
        :return: The list of receipts.
        """
        params = {
            'address': address,
            'limit': limit
        }
        url = self.base_url + f'/hotspots/receipts'
        return self.get_request(url, params=params)



