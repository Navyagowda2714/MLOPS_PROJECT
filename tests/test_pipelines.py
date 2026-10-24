import json
from pathlib import Path

import pytest

from src.components.prediction import Predictor
from src.pipeline.predict_pipeline import PredictPipeline
from src.pipeline.train_pipeline import TrainPipeline
from src.utils.exception import PipelineError


def test_training_promotes_a_model_above_threshold(trained):
    config, result = trained
    assert result.best_model_name in config["training"]["models"]
    assert result.best_score >= config["training"]["min_score"]
    assert result.model_path.exists()

    metrics = json.loads((Path(config["artifacts"]["root"]) / "metrics.json").read_text())
    assert metrics["best_model"] == result.best_model_name
    assert set(metrics["results"]) == set(config["training"]["models"])


def test_training_refuses_weak_models(config):
    config["training"]["min_score"] = 1.01  # impossible bar
    with pytest.raises(PipelineError):
        TrainPipeline(config).run()


def test_prediction_matches_known_labels(trained, sample_records):
    config, _ = trained
    X, y = sample_records
    predictions = PredictPipeline(config).predict(X)

    assert len(predictions) == 5
    assert [p["prediction"] for p in predictions] == y
    for p in predictions:
        assert 0.0 <= p["probability_malignant"] <= 1.0
        assert p["label"] in {"malignant", "benign"}


def test_prediction_rejects_missing_features(trained, sample_records):
    config, _ = trained
    X, _ = sample_records
    with pytest.raises(PipelineError, match="Missing features"):
        PredictPipeline(config).predict(X.drop(columns=["mean_radius"]))


def test_predictor_without_training_gives_clear_error(config):
    with pytest.raises(PipelineError, match="Run the training pipeline first"):
        Predictor(config).load()
