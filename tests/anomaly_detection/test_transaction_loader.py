import pytest
import responses

from anomaly_detection.transaction_loader import (
    TransactionLoader,
    TransactionLoadingError,
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
