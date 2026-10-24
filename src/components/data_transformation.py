"""Stage 3 — impute and scale features. The preprocessor is fitted on train data only."""
from dataclasses import dataclass
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.impute import SimpleImputer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

from src.utils.common import resolve, save_object
from src.utils.logger import logger


@dataclass
class TransformationArtifact:
    X_train: np.ndarray
    y_train: np.ndarray
    X_test: np.ndarray
    y_test: np.ndarray
    feature_names: list
    preprocessor_path: Path


def build_preprocessor() -> Pipeline:
    return Pipeline([
        ("imputer", SimpleImputer(strategy="median")),
        ("scaler", StandardScaler()),
    ])


class DataTransformation:
    def __init__(self, config: dict):
        self.target = config["data"]["target_column"]
        self.preprocessor_path = resolve(config["artifacts"]["root"]) / config["artifacts"]["preprocessor"]

    def run(self, train_path, test_path) -> TransformationArtifact:
        train_df, test_df = pd.read_csv(train_path), pd.read_csv(test_path)
        X_train, y_train = train_df.drop(columns=[self.target]), train_df[self.target].to_numpy()
        X_test, y_test = test_df.drop(columns=[self.target]), test_df[self.target].to_numpy()

        preprocessor = build_preprocessor()
        X_train_t = preprocessor.fit_transform(X_train)  # fit on train only -> no leakage
        X_test_t = preprocessor.transform(X_test)

        save_object(preprocessor, self.preprocessor_path)
        logger.info("Preprocessor fitted on %d features, saved to %s", X_train.shape[1], self.preprocessor_path)
        return TransformationArtifact(
            X_train_t, y_train, X_test_t, y_test, list(X_train.columns), self.preprocessor_path
        )
