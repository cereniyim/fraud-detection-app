from typing import Optional

from pydantic import BaseModel


class AnomalyDetectionInput(BaseModel):
    """
    Input model for anomaly detection.

    Either (`start_block`, `end_block`) or `time_interval_in_seconds` are required.

    If `time_interval_in_seconds` is given, then app runs for the latest blocks within the time interval.

    """
    start_block: Optional[int] = None
    end_block: Optional[int] = None
    time_interval_in_seconds: Optional[int] = 0
    use_pre_trained_model: bool = False


class AnomalyDetectionOutput(BaseModel):
    transaction_hash: str
    value: str
    token: str
    gas_cost: str
    anomaly_score: str
    etherscan_link: str
