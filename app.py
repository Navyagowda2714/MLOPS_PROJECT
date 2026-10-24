"""Flask serving app for the promoted model.

    GET  /health   -> {"status": "ok", "model_loaded": true}
    GET  /features -> list of expected feature names
    POST /predict  -> {"records": [{feature: value, ...}, ...]}  or a single record object
"""
from flask import Flask, jsonify, request

from src.pipeline.predict_pipeline import PredictPipeline
from src.utils.exception import PipelineError

app = Flask(__name__)
_pipeline: PredictPipeline | None = None


def get_pipeline() -> PredictPipeline:
    global _pipeline
    if _pipeline is None:
        _pipeline = PredictPipeline()
    return _pipeline


@app.get("/health")
def health():
    try:
        get_pipeline().predictor.load()
        return jsonify(status="ok", model_loaded=True)
    except PipelineError as exc:
        return jsonify(status="degraded", model_loaded=False, detail=str(exc)), 503


@app.get("/features")
def features():
    return jsonify(features=get_pipeline().predictor.feature_names)


@app.post("/predict")
def predict():
    payload = request.get_json(silent=True)
    if not payload:
        return jsonify(error="Send a JSON object or {'records': [...]}"), 400
    records = payload.get("records", [payload]) if isinstance(payload, dict) else payload
    try:
        return jsonify(predictions=get_pipeline().predict(records))
    except PipelineError as exc:
        return jsonify(error=str(exc)), 422


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
