from dataclasses import dataclass

import numpy as np
import pandas as pd
from sklearn.tree import ExtraTreeRegressor



_WEI_TO_ETH = 10 ** 18


@dataclass
class ModelMetaData:
    estimator: ExtraTreeRegressor #T ODO object from the scikit learn
    model_path: str
    model_name: str


class AnomalyDetector:
    def __init__(self):
        pass

    def fit(self, data: pd.DataFrame) -> ModelMetaData:
        # trains a model
        # pickles model into the local filesystem
        # return ModelMetaData
        # use non-transformed data
        # for visualization use log
        pass

    def predict(self, data: np.ndarray, model_metadata: ModelMetaData = None, pre_trained: bool = False) -> pd.DataFrame:
        # loads most recent model if pre_trained is True
        # if pretrained is False uses model from ModelMetaData
        # predicts on the model
        pass

    def _process_data(self, tx_data: pd.DataFrame) -> pd.DataFrame:
        tx_data = tx_data.dropna(subset=["token", "value", "gas_used", "gas_price"], how="any")
        tx_data = tx_data.drop_duplicates().reset_index(drop=True) # just in case data has any duplicates
        tx_data["gas_cost_in_eth"] = (tx_data["gas_used"] * tx_data["gas_price"]) / _WEI_TO_ETH
        return tx_data
