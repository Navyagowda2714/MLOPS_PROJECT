import copy
import os
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
os.environ.setdefault("LOG_DIR", str(ROOT / "logs"))

from src.utils.common import read_yaml  # noqa: E402


@pytest.fixture()
def config(tmp_path):
    """Real config, but every artifact is written to a temp dir."""
    cfg = copy.deepcopy(read_yaml())
    cfg["artifacts"]["root"] = str(tmp_path / "artifacts")
    return cfg


@pytest.fixture()
def trained(config):
    from src.pipeline.train_pipeline import TrainPipeline

    result = TrainPipeline(config).run()
    return config, result


@pytest.fixture()
def sample_records():
    import pandas as pd

    df = pd.read_csv(ROOT / "data" / "breast_cancer.csv")
    return df.drop(columns=["target"]).head(5), df["target"].head(5).tolist()
