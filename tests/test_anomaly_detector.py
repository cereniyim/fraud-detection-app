import pandas as pd

from anomaly_detection.model_trainer import AnomalyDetector
import pandas.testing as pdt


def test_process_data():
    data = pd.DataFrame({
        "tx_hash": ["hash1", "hash1", "hash2", "hash3", "hash4"],
        "value": [1000000, 1000000, 2000000, 3000000, 3000000],
        "token": ["TokenA", "TokenA", "TokenB", "TokenA", None],
        "gas_used": [50000, 50000, 60000, 70000, 70000],
        "gas_price": [10, 10, 12, 15, None]
    })

    expected = pd.DataFrame(
        {
            "tx_hash": ["hash1", "hash2", "hash3"],
            "value": [1000000, 2000000, 3000000,],
            "token": ["TokenA", "TokenB", "TokenA"],
            "gas_used": [50000, 60000, 70000],
            "gas_price": [10, 12, 15],
            "gas_cost_in_eth": [5000*10/(10 ** 18), 6000*12/(10 ** 18), 70000*15/(10 ** 18)]
        }
    )

    detector = AnomalyDetector()
    res = detector._process_data(data)

    pdt.assert_frame_equal(expected, res, check_dtype=False)