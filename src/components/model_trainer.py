"""Stage 4 — train candidate models, compare them on the test set and promote the best one."""
from dataclasses import dataclass
from pathlib import Path

from sklearn.ensemble import GradientBoostingClassifier, RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, f1_score, precision_score, recall_score, roc_auc_score

from src.utils.common import resolve, save_json, save_object
from src.utils.exception import PipelineError
from src.utils.logger import logger

MODEL_REGISTRY = {
    "logistic_regression": LogisticRegression,
    "random_forest": RandomForestClassifier,
    "gradient_boosting": GradientBoostingClassifier,
}


@dataclass
class TrainerArtifact:
    best_model_name: str
    best_score: float
    metrics: dict
    model_path: Path


def evaluate(model, X, y, positive_label: int) -> dict:
    y_pred = model.predict(X)
    # probability of the positive (costly) class for ROC-AUC
    pos_index = list(model.classes_).index(positive_label)
    y_score = model.predict_proba(X)[:, pos_index]
    return {
        "accuracy": round(accuracy_score(y, y_pred), 4),
        "precision": round(precision_score(y, y_pred, pos_label=positive_label), 4),
        "recall": round(recall_score(y, y_pred, pos_label=positive_label), 4),
        "f1": round(f1_score(y, y_pred, pos_label=positive_label), 4),
        "roc_auc": round(roc_auc_score((y == positive_label).astype(int), y_score), 4),
    }


class ModelTrainer:
    def __init__(self, config: dict):
        self.cfg = config["training"]
        self.random_state = config["data"]["random_state"]
        root = resolve(config["artifacts"]["root"])
        self.model_path = root / config["artifacts"]["model"]
        self.metrics_path = root / config["artifacts"]["metrics"]

    def _build(self, name: str, params: dict):
        cls = MODEL_REGISTRY[name]
        if "random_state" in cls().get_params():
            params = {**params, "random_state": self.random_state}
        return cls(**params)

    def run(self, X_train, y_train, X_test, y_test) -> TrainerArtifact:
        metric = self.cfg["selection_metric"]
        results, fitted = {}, {}
        for name, params in self.cfg["models"].items():
            model = self._build(name, params or {})
            model.fit(X_train, y_train)
            results[name] = evaluate(model, X_test, y_test, self.cfg["positive_label"])
            fitted[name] = model
            logger.info("%-20s %s", name, results[name])

        # rank on the selection metric, break ties with ROC-AUC
        best_name = max(results, key=lambda n: (results[n][metric], results[n]["roc_auc"]))
        best_score = results[best_name][metric]
        if best_score < self.cfg["min_score"]:
            raise PipelineError(f"Best model {best_name} has {metric}={best_score} < min_score {self.cfg['min_score']}")

        save_object(fitted[best_name], self.model_path)
        save_json({"selection_metric": metric, "best_model": best_name, "results": results}, self.metrics_path)
        logger.info("Promoted %s (%s=%.4f) -> %s", best_name, metric, best_score, self.model_path)
        return TrainerArtifact(best_name, best_score, results, self.model_path)
