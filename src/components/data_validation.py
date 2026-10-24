"""Stage 2 — check the split data before any model sees it."""
from dataclasses import dataclass, field

import pandas as pd

from src.utils.common import resolve, save_json
from src.utils.exception import PipelineError
from src.utils.logger import logger


@dataclass
class ValidationReport:
    passed: bool
    checks: dict = field(default_factory=dict)


class DataValidation:
    def __init__(self, config: dict):
        self.cfg = config["validation"]
        self.target = config["data"]["target_column"]
        self.report_path = resolve(config["artifacts"]["root"]) / config["artifacts"]["validation_report"]

    def validate(self, train_df: pd.DataFrame, test_df: pd.DataFrame) -> ValidationReport:
        checks = {
            "target_present": self.target in train_df.columns and self.target in test_df.columns,
            "same_columns": list(train_df.columns) == list(test_df.columns),
            "enough_rows": len(train_df) >= self.cfg["min_rows"],
            "features_numeric": all(
                pd.api.types.is_numeric_dtype(train_df[c]) for c in train_df.columns if c != self.target
            ),
        }
        missing_ratio = train_df.isna().mean()
        checks["missing_values_ok"] = bool((missing_ratio <= self.cfg["max_missing_ratio"]).all())
        if checks["target_present"]:
            observed = set(train_df[self.target].unique()) | set(test_df[self.target].unique())
            checks["target_values_ok"] = observed <= set(self.cfg["allowed_target_values"])
        else:
            checks["target_values_ok"] = False

        report = ValidationReport(passed=all(checks.values()), checks=checks)
        save_json({"passed": report.passed, "checks": checks}, self.report_path)
        logger.info("Validation %s: %s", "PASSED" if report.passed else "FAILED", checks)
        return report

    def run(self, train_path, test_path) -> ValidationReport:
        report = self.validate(pd.read_csv(train_path), pd.read_csv(test_path))
        if not report.passed:
            failed = [name for name, ok in report.checks.items() if not ok]
            raise PipelineError(f"Data validation failed: {failed}")
        return report
