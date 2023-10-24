import logging
import os
import pickle
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

import pandas as pd
from sklearn.ensemble import IsolationForest

_WEI_TO_ETH = 10**18


class ModelLoadingError(Exception):
    pass


@dataclass
class ModelMetaData:
    estimator: IsolationForest
    model_path: str


class AnomalyDetector:
    def __init__(self, estimator: IsolationForest = None):
        self._estimator = estimator or IsolationForest(
            random_state=42,
            contamination=0.001,
        )
        self._features = ["value", "gas_cost_in_eth"]
        self._models_directory = Path(__file__).parents[0] / "models"
        if not self._models_directory.exists():
            # local filesystem serves as a model registry, so create the directory upon instantiation
            os.mkdir(self._models_directory)

    def fit_and_save_model(self, data: pd.DataFrame) -> ModelMetaData:
        """
        Fit the anomaly detection model with the input data and save it to model registry

        Parameters
        ----------
        data: pd.DataFrame
            must have `value` and `gas_cost_in_eth` columns

        Returns
        -------
        ModelMetaData: Metadata for the fitted model
            stores the fitted estimator and the model_path

        """
        features = data[self._features]
        fitted_estimator = self._estimator.fit(features)
        timestamp = int(datetime.now().timestamp())
        filename = f"model_{timestamp}.pkl"
        model_path = str(self._models_directory / filename)
        with open(model_path, "wb") as model_file:
            pickle.dump(fitted_estimator, model_file)
        return ModelMetaData(estimator=fitted_estimator, model_path=model_path)

    def predict(
        self,
        data: pd.DataFrame,
        model_metadata: ModelMetaData = None,
        use_pre_trained_model: bool = False,
    ) -> pd.DataFrame:
        """
        Generate predictions for detecting anomalous transactions using input data. If `use_pre_trained_model` is True,
        then the latest model is loaded from the registry and used. Otherwise, `ModelMetaData.fitted_estimator` is used.

        Parameters
        ----------
        data: pd.DataFrame
            must have `value` and  `gas_cost_in_eth` columns
        model_metadata: ModelMetaData
        use_pre_trained_model: bool
            default False

        Raises
        -------
        ModelLoadingError
            If no models are available in the model registry

        Returns
        -------
        data: pd.DataFrame with `anomaly` and `anomaly_score` columns added
            labeled data as anomalous or not, `anomaly` is equal to -1 for the anomalous data

        """
        models = os.listdir(self._models_directory)
        if use_pre_trained_model and len(models) == 0:
            raise ModelLoadingError(
                "No models found in the registry, train a model first to use a pre-trained one."
            )
        elif use_pre_trained_model and len(models) > 0:
            latest_model_filename = sorted(models)[-1]
            logging.info(
                f"Using pre-trained model for anomaly detection, latest model is {latest_model_filename}."
            )
            with open(
                str(self._models_directory / latest_model_filename), "rb"
            ) as model_file:
                estimator = pickle.load(model_file)
        else:
            estimator = model_metadata.estimator
        data["anomaly"] = estimator.predict(data[self._features])
        data["anomaly_score"] = -1 * estimator.score_samples(data[self._features])
        # to align scoring logic with the original paper
        return data

    @staticmethod
    def process_data(tx_data: pd.DataFrame) -> pd.DataFrame:
        """
        Processes input data
            - removes rows with at least one NA value
            - drops duplicate rows
            - adds `gas_cost_in_eth` feature to data

        Parameters
        ----------
        tx_data: pd.DataFrame
            must have `token`, `value`, `gas_used` and `gas_price` columns

        Returns
        -------
        tx_data: pd.DataFrame

        """
        tx_data = tx_data.dropna(
            subset=["token", "value", "gas_used", "gas_price"], how="any"
        )
        tx_data = tx_data.drop_duplicates().reset_index(
            drop=True
        )  # just in case, if data has any duplicates
        tx_data["gas_cost_in_eth"] = (
            tx_data["gas_used"] * tx_data["gas_price"]
        ) / _WEI_TO_ETH
        return tx_data
