"""Batch / single-record inference using the promoted model.

Usage:
    python -m src.pipeline.predict_pipeline --input new_records.csv
"""
import argparse

import pandas as pd

from src.components.prediction import Predictor
from src.utils.common import DEFAULT_CONFIG_PATH, read_yaml


class PredictPipeline:
    def __init__(self, config: dict | None = None):
        self.predictor = Predictor(config or read_yaml(DEFAULT_CONFIG_PATH))

    def predict(self, records: list[dict] | pd.DataFrame) -> list[dict]:
        df = records if isinstance(records, pd.DataFrame) else pd.DataFrame(records)
        return self.predictor.predict(df)


def main() -> None:
    parser = argparse.ArgumentParser(description="Score a CSV with the trained model")
    parser.add_argument("--input", required=True, help="CSV with the same feature columns as training data")
    args = parser.parse_args()
    for row in PredictPipeline().predict(pd.read_csv(args.input)):
        print(row)


if __name__ == "__main__":
    main()
