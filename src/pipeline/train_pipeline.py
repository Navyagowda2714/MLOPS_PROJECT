"""End-to-end training: ingestion -> validation -> transformation -> training.

Usage:
    python -m src.pipeline.train_pipeline [--config config/config.yaml]
"""
import argparse

from src.components.data_ingestion import DataIngestion
from src.components.data_transformation import DataTransformation
from src.components.data_validation import DataValidation
from src.components.model_trainer import ModelTrainer, TrainerArtifact
from src.utils.common import DEFAULT_CONFIG_PATH, read_yaml
from src.utils.logger import logger


class TrainPipeline:
    def __init__(self, config: dict | None = None):
        self.config = config or read_yaml(DEFAULT_CONFIG_PATH)

    def run(self) -> TrainerArtifact:
        logger.info("===== Training pipeline started =====")
        ingestion = DataIngestion(self.config).run()
        DataValidation(self.config).run(ingestion.train_path, ingestion.test_path)
        data = DataTransformation(self.config).run(ingestion.train_path, ingestion.test_path)
        result = ModelTrainer(self.config).run(data.X_train, data.y_train, data.X_test, data.y_test)
        logger.info("===== Training pipeline finished: %s =====", result.best_model_name)
        return result


def main() -> None:
    parser = argparse.ArgumentParser(description="Run the training pipeline")
    parser.add_argument("--config", default=str(DEFAULT_CONFIG_PATH))
    args = parser.parse_args()
    result = TrainPipeline(read_yaml(args.config)).run()
    print(f"Best model: {result.best_model_name}")
    for name, metrics in result.metrics.items():
        print(f"  {name:<20} {metrics}")


if __name__ == "__main__":
    main()
