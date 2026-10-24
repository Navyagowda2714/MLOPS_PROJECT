import pandas as pd
import pytest

from src.components.data_ingestion import DataIngestion
from src.components.data_transformation import DataTransformation
from src.components.data_validation import DataValidation
from src.utils.exception import PipelineError


def test_ingestion_creates_stratified_split(config):
    artifact = DataIngestion(config).run()
    train, test = pd.read_csv(artifact.train_path), pd.read_csv(artifact.test_path)

    assert len(train) + len(test) == 569
    assert len(test) == pytest.approx(569 * config["data"]["test_size"], abs=1)
    # stratified: class balance is preserved in both splits
    assert train["target"].mean() == pytest.approx(test["target"].mean(), abs=0.02)


def test_ingestion_fails_on_missing_file(config):
    config["data"]["source_path"] = "data/does_not_exist.csv"
    with pytest.raises(PipelineError):
        DataIngestion(config).run()


def test_validation_passes_on_clean_data(config):
    artifact = DataIngestion(config).run()
    report = DataValidation(config).run(artifact.train_path, artifact.test_path)
    assert report.passed and all(report.checks.values())


@pytest.mark.parametrize(
    "corrupt, failed_check",
    [
        (lambda df: df.drop(columns=["target"]), "target_present"),
        (lambda df: df.assign(target=df["target"].replace(1, 7)), "target_values_ok"),
        (lambda df: df.assign(mean_radius="abc"), "features_numeric"),
        (lambda df: df.assign(mean_radius=None), "missing_values_ok"),
    ],
)
def test_validation_catches_bad_data(config, corrupt, failed_check):
    artifact = DataIngestion(config).run()
    train = corrupt(pd.read_csv(artifact.train_path))
    test = pd.read_csv(artifact.test_path)
    if failed_check == "target_present":
        test = test.drop(columns=["target"])
    report = DataValidation(config).validate(train, test)
    assert not report.passed
    assert report.checks[failed_check] is False


def test_transformation_fits_scaler_on_train_only(config):
    artifact = DataIngestion(config).run()
    data = DataTransformation(config).run(artifact.train_path, artifact.test_path)

    assert data.X_train.shape[1] == data.X_test.shape[1] == 30
    # standardised train features have ~0 mean; test is close but not forced to 0
    assert abs(data.X_train.mean()) < 1e-6
    assert data.preprocessor_path.exists()
