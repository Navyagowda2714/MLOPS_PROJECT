"""Stage 1 — read the raw dataset and create a stratified train/test split."""
from dataclasses import dataclass
from pathlib import Path

import pandas as pd
from sklearn.model_selection import train_test_split

from src.utils.common import resolve
from src.utils.exception import PipelineError
from src.utils.logger import logger


@dataclass
class IngestionArtifact:
    train_path: Path
    test_path: Path


class DataIngestion:
    def __init__(self, config: dict):
        self.data_cfg = config["data"]
        self.artifacts_dir = resolve(config["artifacts"]["root"])
        self.train_file = config["artifacts"]["train_file"]
        self.test_file = config["artifacts"]["test_file"]

    def run(self) -> IngestionArtifact:
        source = resolve(self.data_cfg["source_path"])
        if not source.exists():
            raise PipelineError(f"Dataset not found: {source}")

        df = pd.read_csv(source)
        logger.info("Loaded %d rows x %d columns from %s", *df.shape, source)

        target = self.data_cfg["target_column"]
        train_df, test_df = train_test_split(
            df,
            test_size=self.data_cfg["test_size"],
            random_state=self.data_cfg["random_state"],
            stratify=df[target],
        )

        self.artifacts_dir.mkdir(parents=True, exist_ok=True)
        train_path = self.artifacts_dir / self.train_file
        test_path = self.artifacts_dir / self.test_file
        train_df.to_csv(train_path, index=False)
        test_df.to_csv(test_path, index=False)
        logger.info("Train: %d rows -> %s | Test: %d rows -> %s", len(train_df), train_path, len(test_df), test_path)
        return IngestionArtifact(train_path, test_path)
