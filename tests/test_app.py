import pytest

import app as app_module
from src.pipeline.predict_pipeline import PredictPipeline


@pytest.fixture()
def client(trained, monkeypatch):
    config, _ = trained
    monkeypatch.setattr(app_module, "_pipeline", PredictPipeline(config))
    return app_module.app.test_client()


def test_health(client):
    assert client.get("/health").get_json() == {"status": "ok", "model_loaded": True}


def test_features_endpoint(client):
    features = client.get("/features").get_json()["features"]
    assert len(features) == 30 and "mean_radius" in features


def test_predict_single_and_batch(client, sample_records):
    X, y = sample_records
    records = X.to_dict(orient="records")

    single = client.post("/predict", json=records[0])
    assert single.status_code == 200
    assert single.get_json()["predictions"][0]["prediction"] == y[0]

    batch = client.post("/predict", json={"records": records})
    assert [p["prediction"] for p in batch.get_json()["predictions"]] == y


def test_predict_bad_requests(client):
    assert client.post("/predict", json={}).status_code == 400
    assert client.post("/predict", json={"mean_radius": 10}).status_code == 422
