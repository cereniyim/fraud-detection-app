from typing import Optional

from pydantic import BaseModel


class AnomalyDetectionInput(BaseModel):
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
