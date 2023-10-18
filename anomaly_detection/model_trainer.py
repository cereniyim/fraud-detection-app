import os
import pickle
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

import pandas as pd
from sklearn.ensemble import IsolationForest


_WEI_TO_ETH = 10 ** 18


@dataclass
class ModelMetaData:
    estimator: IsolationForest
    model_path: str


class AnomalyDetector:
    def __init__(self, estimator=None):
        self._estimator = estimator or IsolationForest(
            random_state=42,
            contamination=0.001,
        )
        self._features = ["value", "gas_cost_in_eth"]
        self._models_directory = Path(__file__).parents[0] / "models"

    def fit(self, data: pd.DataFrame) -> ModelMetaData:
        features = data[self._features]
        fitted_estimator = self._estimator.fit(features)
        timestamp = int(datetime.now().timestamp())
        filename = f"model_{timestamp}.pkl"
        model_path = str(self._models_directory / filename)
        with open(model_path, 'wb') as model_file:
            pickle.dump(fitted_estimator, model_file)
        return ModelMetaData(estimator=fitted_estimator, model_path=model_path)

    def predict(self, data: pd.DataFrame, model_metadata: ModelMetaData = None, pre_trained: bool = False) -> pd.DataFrame:
        if pre_trained:
            latest_model_filename = os.listdir(self._models_directory)[0]
            with open(str(self._models_directory / latest_model_filename), "rb") as model_file:
                estimator = pickle.load(model_file)
        else:
            estimator = model_metadata.estimator
        data["anomaly"] = estimator.predict(data[self._features])
        data["anomaly_score"] = estimator.score_samples(data[self._features])
        return data

    def _process_data(self, tx_data: pd.DataFrame) -> pd.DataFrame:
        tx_data = tx_data.dropna(subset=["token", "value", "gas_used", "gas_price"], how="any")
        tx_data = tx_data.drop_duplicates().reset_index(drop=True) # just in case data has any duplicates
        tx_data["gas_cost_in_eth"] = (tx_data["gas_used"] * tx_data["gas_price"]) / _WEI_TO_ETH
        return tx_data
