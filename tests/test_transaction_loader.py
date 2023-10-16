from unittest.mock import Mock

import pandas as pd
import pytest
import responses
import pandas.testing as pdt

from anomaly_detection.transaction_loader import (
    TransactionLoadingError,
    TransactionLoader,
)

_API_KEY = "t-5jnnHotwe9R3vHAUPcfOY9eYNufREN"


@pytest.fixture()
def get_asset_transfers_response():
    return {
        "jsonrpc": "2.0",
        "id": 1,
        "result": {
            "transfers": [
                {
                    "blockNum": "0x1157358",
                    "uniqueId": "0x12345:log:0",
                    "hash": "0x12345",
                    "from": "0x824a30f2984f9013f2c8d0a29c0a3cc5fd5c0673",
                    "to": "0x51c72848c68a965f66fa7a88855f9f7784502a7f",
                    "value": 25302.294916285482,
                    "erc721TokenId": None,
                    "erc1155Metadata": None,
                    "tokenId": None,
                    "asset": "BLUR",
                    "category": "erc20",
                    "rawContract": {
                        "value": "0x055ba3e1410ec848cd45",
                        "address": "0x5283d291dbcf85356a21ba090e6db59121208b44",
                        "decimal": "0x12",
                    },
                    "metadata": {"blockTimestamp": "2023-09-21T08:15:47.000Z"},
                },
                {
                    "blockNum": "0x1157358",
                    "uniqueId": "0x12345:log:1",
                    "hash": "0x12345",
                    "from": "0x51c72848c68a965f66fa7a88855f9f7784502a7f",
                    "to": "0x824a30f2984f9013f2c8d0a29c0a3cc5fd5c0673",
                    "value": 2.895178921614788,
                    "erc721TokenId": None,
                    "erc1155Metadata": None,
                    "tokenId": None,
                    "asset": "WETH",
                    "category": "erc20",
                    "rawContract": {
                        "value": "0x282dbde3d00c4600",
                        "address": "0xc02aaa39b223fe8d0a0e5c4f27ead9083c756cc2",
                        "decimal": "0x12",
                    },
                    "metadata": {"blockTimestamp": "2023-09-21T08:15:47.000Z"},
                },
                {
                    "blockNum": "0x1157358",
                    "uniqueId": "0x67890:log:3",
                    "hash": "0x67890",
                    "from": "0xfd79505aa075007ef1f1165c4de3562bb48b9bd2",
                    "to": "0x977c5fcf7a552d38adcde4f41025956855497c6d",
                    "value": 11253986.52601218,
                    "erc721TokenId": None,
                    "erc1155Metadata": None,
                    "tokenId": None,
                    "asset": "\u0428\u0410\u0419\u041b\u0423\u0428\u0410\u0419",
                    "category": "erc20",
                    "rawContract": {
                        "value": "0x094f1fd500000000000000",
                        "address": "0xff836a5821e69066c87e268bc51b849fab94240c",
                        "decimal": "0x12",
                    },
                    "metadata": {"blockTimestamp": "2023-09-21T08:15:47.000Z"},
                },
            ],
            "pageKey": "b06d218b-2fa6-4bc0-bde2-495462ea58ef",
        },
    }


@pytest.fixture()
def get_tx_receipts_response():
    return {
        "jsonrpc": "2.0",
        "id": 1,
        "result": {
            "receipts": [
                {
                    "transactionHash": "0x12345",
                    "blockHash": "0xb783e282a35b399aa3ff0db1e0593879de12f40281d249307df1cb5154f5f17f",
                    "blockNumber": "0x1157358",
                    "logs": [],
                    "contractAddress": None,
                    "effectiveGasPrice": "0xa87132cdf",
                    "cumulativeGasUsed": "0x1bbf4",
                    "from": "0xad35ed1cfe7c17c7b06c5c5d0672c57da4925299",
                    "gasUsed": "0x1bbf4",
                    "logsBloom": "0x00000000000000000000000000000000000000000000000000000004000000000000000000000010000000000000000002008000080020000000040000000000000000000000000800000008000800000000000000040000100000000000000000000004000000000000000000000000000000000000000000000010000800000000100000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000800000000000000002000000000000000000000000000000000400000000000000000000000100200000000000000000000000000000000000000000000000000000000000",
                    "status": "0x1",
                    "to": "0x51c72848c68a965f66fa7a88855f9f7784502a7f",
                    "transactionIndex": "0x0",
                    "type": "0x2",
                },
                {
                    "transactionHash": "0x67890",
                    "blockHash": "0xb783e282a35b399aa3ff0db1e0593879de12f40281d249307df1cb5154f5f17f",
                    "blockNumber": "0x1157358",
                    "logs": [],
                    "contractAddress": None,
                    "effectiveGasPrice": "0x54f2cec2f",
                    "cumulativeGasUsed": "0x3f063",
                    "from": "0x0000000000d3e910c999cfa4a016eaafe9fcb604",
                    "gasUsed": "0x2346f",
                    "logsBloom": "0x00200000000000000040000080000000000000000000000102000000000000000000000000000000001000000000000002000000080020000000000000000000000000000000800800000008000000201000000000000000000000000000000000000000000000000000000100000000000000000000000000000010000800000000000000000000000000000000000000004000000080080001004000000000000000000000000000000000000010000000000000000000200000000000000000000002008000000000004000000000000000000000001000000000000000000020200000000000000000000000000000000080400000000000000001000000",
                    "status": "0x1",
                    "to": "0x0000000000c2f3017e5af636ea91bd68ec3888ed",
                    "transactionIndex": "0x1",
                    "type": "0x2",
                },
                {
                    "transactionHash": "not_a_transfer_hash",
                    "blockHash": "0xb783e282a35b399aa3ff0db1e0593879de12f40281d249307df1cb5154f5f17f",
                    "blockNumber": "0x1157358",
                    "logs": [],
                    "contractAddress": None,
                    "effectiveGasPrice": "0x1dc700121",
                    "cumulativeGasUsed": "0xe03309",
                    "from": "0x1f9090aae28b8a3dceadf281b0f12828e676c326",
                    "gasUsed": "0x6556",
                    "logsBloom": "0x00000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000",
                    "status": "0x1",
                    "to": "0xf2a4df2897c69a0bc8f12b2b933893604055705e",
                    "transactionIndex": "0x73",
                    "type": "0x2",
                },
            ]
        },
    }


@responses.activate
def test_get_transfer_txs_success(get_asset_transfers_response):
    responses.add(
        responses.POST,
        f"https://eth-mainnet.g.alchemy.com/v2/{_API_KEY}",
        json=get_asset_transfers_response,
        status=200,
    )

    loader = TransactionLoader(_API_KEY)
    result = loader._get_transfer_txs(1, 2)

    assert result == {
        "0x12345": [(25302.294916285482, "BLUR"), (2.895178921614788, "WETH")],
        "0x67890": [
            (11253986.52601218, "\u0428\u0410\u0419\u041b\u0423\u0428\u0410\u0419")
        ],
    }


@responses.activate
def test_get_transfer_txs_failed():
    responses.add(
        responses.POST,
        f"https://eth-mainnet.g.alchemy.com/v2/{_API_KEY}",
        json={},
        status=404,
    )

    with pytest.raises(TransactionLoadingError):
        res = TransactionLoader(_API_KEY)._get_transfer_txs(1, 2)


@responses.activate
def test_get_tx_receipts_success(get_tx_receipts_response):
    responses.add(
        responses.POST,
        f"https://eth-mainnet.g.alchemy.com/v2/{_API_KEY}",
        json=get_tx_receipts_response,
        status=200,
    )

    loader = TransactionLoader(_API_KEY)
    result = loader._get_tx_receipts(1, 3)

    assert result == {
        "0x12345": {
            "gasUsed": int("0x1bbf4", base=16),
            "effectiveGasPrice": int("0xa87132cdf", base=16),
        },
        "0x67890": {
            "gasUsed": int("0x2346f", base=16),
            "effectiveGasPrice": int("0x54f2cec2f", base=16),
        },
        "not_a_transfer_hash": {
            "effectiveGasPrice": int("0x1dc700121", base=16),
            "gasUsed": int("0x6556", base=16),
        },
    }


def test_load():
    loader = TransactionLoader(_API_KEY)

    loader._get_transfer_txs = Mock(
        return_value={
            "0x12345": [(25302.294916285482, "BLUR"), (2.895178921614788, "WETH")],
            "0x67890": [
                (11253986.52601218, "\u0428\u0410\u0419\u041b\u0423\u0428\u0410\u0419")
            ],
        }
    )
    loader._get_tx_receipts = Mock(
        return_value={
            "0x12345": {
                "gasUsed": int("0x1bbf4", base=16),
                "effectiveGasPrice": int("0xa87132cdf", base=16),
            },
            "0x67890": {
                "gasUsed": int("0x2346f", base=16),
                "effectiveGasPrice": int("0x54f2cec2f", base=16),
            },
            "not_a_transfer_hash": {
                "effectiveGasPrice": int("0x1dc700121", base=16),
                "gasUsed": int("0x6556", base=16),
            },
        }
    )

    res = loader.load(1, 2)

    expected = pd.DataFrame(
        [
            {
                "tx_hash": "0x12345",
                "asset": "BLUR",
                "value": 25302.294916285482,
                "gas_used": 113652,
                "gas_price": 45215853791,
            },
            {
                "tx_hash": "0x12345",
                "asset": "WETH",
                "value": 2.895178921614788,
                "gas_used": 113652,
                "gas_price": 45215853791,
            },
            {
                "tx_hash": "0x67890",
                "asset": "\u0428\u0410\u0419\u041b\u0423\u0428\u0410\u0419",
                "value": 11253986.52601218,
                "gas_used": 144495,
                "gas_price": 22803180591,
            },
        ]
    )

    pdt.assert_frame_equal(res, expected, check_like=True)


# @pytest.mark.skip(reason="requires internet connection")
def test_laod_integration():
    loader = TransactionLoader(_API_KEY)
    res = loader.load(start_block=18362260, end_block=18362263)  # query for 3 blocks

    assert isinstance(res, pd.DataFrame)
    assert len(res) > 0
