import os
import shutil
from pathlib import Path

import pandas as pd
import pandas.testing as pdt
import pytest
from sklearn.ensemble import IsolationForest

from anomaly_detection.anomaly_detector import (
    AnomalyDetector,
    ModelMetaData,
    ModelLoadingError,
)


@pytest.fixture()
def raw_data():
    return pd.DataFrame(
        {
            "tx_hash": ["hash1", "hash1", "hash2", "hash3", "hash4"],
            "value": [1000000, 1000000, 2000000, 3000000, 3000000],
            "token": ["TokenA", "TokenA", "TokenB", "TokenA", None],
            "gas_used": [50000, 50000, 60000, 70000, 70000],
            "gas_price": [10, 10, 12, 15, None],
        }
    )


@pytest.fixture()
def processed_data():
    gas_used = [50000, 60000, 70000]
    gas_price = [10, 12, 15]
    return pd.DataFrame(
        {
            "tx_hash": ["hash1", "hash2", "hash3"],
            "value": [
                1000000,
                2000000,
                3000000,
            ],
            "token": ["TokenA", "TokenB", "TokenA"],
            "gas_used": gas_used,
            "gas_price": gas_price,
            "gas_cost_in_eth": [
                gas * price / (10**18) for gas, price in zip(gas_used, gas_price)
            ],
        }
    )


@pytest.fixture
def remove_models():
    yield
    models = AnomalyDetector()._models_directory
    shutil.rmtree(models)


def test_process_data(raw_data, processed_data):
    detector = AnomalyDetector()
    res = detector.process_data(raw_data)

    pdt.assert_frame_equal(processed_data, res, check_dtype=False)


@pytest.mark.usefixtures("remove_models")
def test_fit_and_save_model(processed_data):
    detector = AnomalyDetector()
    res = detector.fit_and_save_model(processed_data)

    assert isinstance(res, ModelMetaData)
    assert isinstance(res.estimator, IsolationForest)
    assert isinstance(res.model_path, str)
    assert Path(res.model_path).exists()


@pytest.mark.usefixtures("remove_models")
def test_predict_from_pretrained_model_raises(processed_data):
    detector = AnomalyDetector()

    assert len(os.listdir(detector._models_directory)) == 0

    with pytest.raises(ModelLoadingError):
        res = AnomalyDetector().predict(data=processed_data, use_pre_trained_model=True)


@pytest.mark.usefixtures("remove_models")
def test_predict_from_pretrained_model(processed_data):
    detector = AnomalyDetector()
    _ = detector.fit_and_save_model(processed_data)
    res = AnomalyDetector().predict(data=processed_data, use_pre_trained_model=True)

    assert isinstance(res, pd.DataFrame)
    assert "anomaly_score" in res.columns
    assert "anomaly" in res.columns


@pytest.mark.usefixtures("remove_models")
def test_predict_from_model_metadata(processed_data):
    fitted_model = IsolationForest(random_state=42, contamination=0.001).fit(
        processed_data[["value", "gas_cost_in_eth"]]
    )
    detector = AnomalyDetector()
    model_metadata = ModelMetaData(estimator=fitted_model, model_path="some_path")
    res = detector.predict(data=processed_data, model_metadata=model_metadata)

    assert isinstance(res, pd.DataFrame)
    assert "anomaly_score" in res.columns
    assert "anomaly" in res.columns
