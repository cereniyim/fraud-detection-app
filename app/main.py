from fastapi import FastAPI, HTTPException

from anomaly_detection.anomaly_detector import AnomalyDetector, ModelLoadingError
from anomaly_detection.transaction_loader import (
    TransactionLoader,
    TransactionLoadingError,
)
from app.data_models import AnomalyDetectionInput, AnomalyDetectionOutput


app = FastAPI(
    responses={
        500: {"description": "Error during anomaly detection"},
        404: {"description": "Model not found in the registry"},
    }
)


@app.post("/anomaly_detection/")
def post_item(
    anomaly_detection_input: AnomalyDetectionInput,
) -> list[AnomalyDetectionOutput]:
    """
    Detect anomalous transactions on Ethereum Mainnet
    """
    loader = TransactionLoader(api_key="t-5jnnHotwe9R3vHAUPcfOY9eYNufREN")
    try:
        transactions = loader.load(
            anomaly_detection_input.start_block,
            anomaly_detection_input.end_block,
            anomaly_detection_input.time_interval_in_seconds,
        )
    except TransactionLoadingError as e:
        raise HTTPException(status_code=500, detail=str(e))

    anomaly_detector = AnomalyDetector()
    processed_transactions = anomaly_detector.process_data(transactions)

    if anomaly_detection_input.use_pre_trained_model:
        try:
            predicted_transactions = anomaly_detector.predict(
                data=processed_transactions,
                use_pre_trained_model=anomaly_detection_input.use_pre_trained_model,
            )
        except ModelLoadingError as e:
            raise HTTPException(status_code=404, detail=str(e))
    else:
        model_metadata = anomaly_detector.fit(processed_transactions)
        predicted_transactions = anomaly_detector.predict(
            data=processed_transactions, model_metadata=model_metadata
        )

    anomalous_transactions = predicted_transactions[
        predicted_transactions["anomaly"] == -1
    ]
    results = []
    for _, row in anomalous_transactions.iterrows():
        results.append(
            AnomalyDetectionOutput(
                transaction_hash=row["tx_hash"],
                value=f"{row['value']:,.2f}",
                token=row["token"],
                gas_cost=f"{row['gas_cost_in_eth']:.8f}",
                anomaly_score=f"{row['anomaly_score']:.4f}",
                etherscan_link=f"https://etherscan.io/tx/{row['tx_hash']}",
            )
        )
    return results
