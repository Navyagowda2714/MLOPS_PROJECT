"""Stage 5 — load the promoted artifacts and score new records."""
from pathlib import Path

import pandas as pd

from src.utils.common import load_object, resolve
from src.utils.exception import PipelineError

CLASS_LABELS = {0: "malignant", 1: "benign"}


class Predictor:
    def __init__(self, config: dict):
        root = resolve(config["artifacts"]["root"])
        self.preprocessor_path = root / config["artifacts"]["preprocessor"]
        self.model_path = root / config["artifacts"]["model"]
        self.positive_label = config["training"]["positive_label"]
        self._preprocessor = None
        self._model = None

    def load(self) -> "Predictor":
        for path in (self.preprocessor_path, self.model_path):
            if not Path(path).exists():
                raise PipelineError(f"Missing artifact {path}. Run the training pipeline first.")
        self._preprocessor = load_object(self.preprocessor_path)
        self._model = load_object(self.model_path)
        return self

    @property
    def feature_names(self) -> list:
        if self._preprocessor is None:
            self.load()
        return list(self._preprocessor.feature_names_in_)

    def predict(self, records: pd.DataFrame) -> list[dict]:
        if self._model is None:
            self.load()
        missing = [c for c in self.feature_names if c not in records.columns]
        if missing:
            raise PipelineError(f"Missing features: {missing}")

        X = self._preprocessor.transform(records[self.feature_names])
        preds = self._model.predict(X)
        pos_index = list(self._model.classes_).index(self.positive_label)
        probs = self._model.predict_proba(X)[:, pos_index]
        return [
            {
                "prediction": int(p),
                "label": CLASS_LABELS.get(int(p), str(p)),
                f"probability_{CLASS_LABELS[self.positive_label]}": round(float(prob), 4),
            }
            for p, prob in zip(preds, probs)
        ]
