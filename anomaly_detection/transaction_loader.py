import logging
from math import ceil
from typing import Optional

import pandas as pd
import requests
from requests import Response, HTTPError


class TransactionLoadingError(Exception):
    pass


_BLOCK_PER_SECOND = 5 / 60


class TransactionLoader:
    def __init__(self, api_key: str = "t-5jnnHotwe9R3vHAUPcfOY9eYNufREN"):
        self._uri = f"https://eth-mainnet.g.alchemy.com/v2/{api_key}"
        self._get_transfer_tx_method_name = "alchemy_getAssetTransfers"
        self._get_tx_receipts_method_name = "alchemy_getTransactionReceipts"
        self._headers = {
            "accept": "application/json",
            "content-type": "application/json",
        }

    def load(
        self,
        start_block: Optional[int] = None,
        end_block: Optional[int] = None,
        time_interval: int = 0,
    ) -> pd.DataFrame:
        """
        Loads ERC20 and external Transfer transactions from Ethereum Mainnet either for the
            - given block range
            - latest blocks within the specified time interval ~ approximately

        Parameters
        ----------
        start_block: Optional[int]
            lower bound block number (inclusive)
        end_block: Optional[int]
            upper bound block number (inclusive)
        time_interval: Optional[int]
            time interval in seconds

        Raises
        -------
        TransactionLoadingError
            If any of the requests to Alchemy endpoints fail

        Returns
        -------
        pd.DataFrame
            Transactions with the amount transferred, gas usage and gas_price
            Each row is unique per token transferred and tx_hash

        tx_hash     |   value   |   token   |   gas_used    |   gas_price

        """
        if time_interval > 0:
            # if time interval is given, we get the start and end block from it
            last_blocks = ceil(time_interval * _BLOCK_PER_SECOND)
            block_response = requests.post(
                self._uri,
                json={
                    "jsonrpc": "2.0",
                    "method": "eth_blockNumber",
                    "params": [],
                    "id": 1,
                },
            )
            self._handle_response_errors(block_response)
            latest_block_number = int(block_response.json()["result"], base=16)
            end_block = latest_block_number - 1
            # alchemy_getTransactionReceipts endpoint fails time to time for the latest block
            # to prevent fallback to latest_block -1
            start_block = end_block - last_blocks + 1
        transfer_txs = self._get_transfer_txs(start_block, end_block)
        tx_gas = self._get_gas_values(start_block, end_block)
        tx_hash2token_and_value = [
            {"tx_hash": key, "value": value[0], "token": value[1]}
            for key, values in transfer_txs.items()
            for value in values
        ]
        df = pd.DataFrame(tx_hash2token_and_value)
        df["gas_used"] = df["tx_hash"].map(lambda x: tx_gas.get(x)["gasUsed"])
        df["gas_price"] = df["tx_hash"].map(
            lambda x: tx_gas.get(x)["effectiveGasPrice"]
        )
        logging.info(f"Loaded transfer transactions from {start_block} to {end_block}")
        return df

    def _get_transfer_txs(
        self,
        start_block: int,
        end_block: int,
    ) -> dict[str, list[tuple[float, str]]]:
        transfers = []
        payload = {
            "id": 1,
            "jsonrpc": "2.0",
            "method": self._get_transfer_tx_method_name,
            "params": [
                {
                    "fromBlock": hex(start_block),
                    "toBlock": hex(end_block),
                    "category": ["external", "erc20"],
                    "excludeZeroValue": True,
                    "maxCount": hex(1000),
                }
            ],
        }
        response = requests.post(self._uri, json=payload, headers=self._headers)
        self._handle_response_errors(response)

        transfers.extend(response.json()["result"]["transfers"])
        page_key = response.json()["result"].get("pageKey")

        while page_key:
            payload["params"][0]["pageKey"] = page_key
            response = requests.post(self._uri, json=payload, headers=self._headers)
            self._handle_response_errors(response)
            response_data = response.json()["result"]
            transfers.extend(response_data["transfers"])
            page_key = response_data.get("pageKey")

        unique_tx_hashes = {t["hash"] for t in transfers}
        result = {tx_hash: [] for tx_hash in unique_tx_hashes}
        for transfer in transfers:
            result[transfer["hash"]].append((transfer["value"], transfer["asset"]))
        return result

    def _get_gas_values(
        self,
        start_block: int,
        end_block: int,
    ) -> dict:
        params = [
            {"blockNumber": hex(block_number)}
            for block_number in range(start_block, end_block + 1)
        ]
        payload = {
            "id": 1,
            "jsonrpc": "2.0",
            "method": self._get_tx_receipts_method_name,
        }
        receipts = []
        for param in params:
            payload["params"] = [param]
            response = requests.post(self._uri, json=payload, headers=self._headers)
            self._handle_response_errors(response)
            receipts.extend(response.json()["result"]["receipts"])
        result = {
            r["transactionHash"]: {
                "gasUsed": int(r["gasUsed"], base=16),
                "effectiveGasPrice": int(r["effectiveGasPrice"], base=16),
            }
            for r in receipts
        }
        return result

    def _handle_response_errors(self, response: Response):
        """
        solution is from https://stackoverflow.com/a/24531618/15485553
        """
        try:
            response.raise_for_status()
        except HTTPError:
            raise TransactionLoadingError("Error in loading data from Alchemy")
