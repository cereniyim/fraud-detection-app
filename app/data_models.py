from typing import Optional

from pydantic import BaseModel


class AnomalyDetectionInput(BaseModel):
    start_block: Optional[int] = None
    end_block: Optional[int] = None
    time_interval: Optional[int] = None
    pre_trained: bool = False


class AnomalyDetectionOutput(BaseModel):
    transaction_hash: str
    value: float
    token: str
    gas_cost: float
    anomaly_score: float
    etherscan_link: str
