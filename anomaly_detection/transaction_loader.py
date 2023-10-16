from typing import Optional

import pandas as pd
import requests
from requests import Response, HTTPError


class TransactionLoadingError(Exception):
    pass


class TransactionLoader:
    """
    1. Loads ERC20 and external transfer transactions for the given block range
        in MVP version support only having a block range
        get tx hashes from that
        "alchemy_getAssetTransfers"
        BEWARE of pagination here with pageKey str
        keep only tx_hash and value dict here

    load until there is no "pageKey" in ["result"]["pageKey"]

    2. Loads tx receipts to get gas "alchemy_getTransactionReceipts" per block
        keep only tx_hash, gasUsed, effectiveGasPrice here

    BEWARE OF hex int conversion

    filter tx receipts with the erc20 ones only return a list of dict with the following format

    [{"tx_hash": "0x0", "value":1, "gas":2, "gas_price": 3}, {"tx_hash": "0x1", "value":1, "gas":2, "gas_price": 3}]

    returns a df with tx, tx_value, gas and gas_price

    3. if timeframe is passed then make an app

    block_per_minute = 5
    "latest"  - passed number * block_per_minute
    """

    def __init__(self, api_key: str):
        self._uri = f"https://eth-mainnet.g.alchemy.com/v2/{api_key}"
        self._get_transfer_tx_method_name = "alchemy_getAssetTransfers"
        self._get_tx_receipts_method_name = "alchemy_getTransactionReceipts"
        self._get_block_number_method_name = "eth_blockNumber"
        self._headers = {
            "accept": "application/json",
            "content-type": "application/json",
        }

    def load(
        self, start_block: int, end_block: int, time_interval: Optional[int] = None
    ) -> pd.DataFrame:
        # erc20_txs = self._get_transfer_txs()
        # tx_receipts = self._get_tx_receipts()
        # filter tx receipts with the erc20 tx hashes
        # make a list of dicts in the following format
        # [{"tx_hash": "0x0", "value":1, "gas":2, "gas_price": 3}, {"tx_hash": "0x1", "value":1, "gas":2, "gas_price": 3}]
        # make a dataframe and return it
        pass

    def _get_transfer_txs(
        self,
        start_block: int,
        end_block: int,
        tx_types: list[str] = ["external", "tx_type"],
    ) -> dict[str, list[tuple[float, str]]]:
        payload = {
            "id": 1,
            "jsonrpc": "2.0",
            "method": self._get_transfer_tx_method_name,
            "params": [
                {
                    "fromBlock": hex(start_block),
                    "toBlock": hex(end_block),
                    "category": tx_types,
                    "excludeZeroValue": True,
                    "maxCount": hex(1000),
                }
            ],
        }
        response = requests.post(self._uri, json=payload, headers=self._headers)
        self._handle_response_errors(response)
        # TODO handle pagination here with the pageKey
        transfers = response.json()["result"]["transfers"]
        unique_tx_hashes = {t["hash"] for t in transfers}
        result = {tx_hash: [] for tx_hash in unique_tx_hashes}
        for transfer in transfers:
            result[transfer["hash"]].append((transfer["value"], transfer["asset"]))
        return result

    def _get_tx_receipts(self) -> dict:
        pass

    def _handle_response_errors(self, response: Response):
        """
        solution is from https://stackoverflow.com/a/24531618/15485553
        """
        try:
            response.raise_for_status()
        except HTTPError:
            raise TransactionLoadingError("Error in loading data from ALchemy")
