"""Scaffold the project layout. Safe to re-run: existing files are never overwritten."""
from pathlib import Path

DIRECTORIES = ["src/components", "src/pipeline", "src/utils", "config", "data", "tests", ".github/workflows"]

FILES = [
    "src/__init__.py",
    "src/components/__init__.py",
    "src/components/data_ingestion.py",
    "src/components/data_validation.py",
    "src/components/data_transformation.py",
    "src/components/model_trainer.py",
    "src/components/prediction.py",
    "src/pipeline/__init__.py",
    "src/pipeline/train_pipeline.py",
    "src/pipeline/predict_pipeline.py",
    "src/utils/__init__.py",
    "src/utils/logger.py",
    "src/utils/common.py",
    "src/utils/exception.py",
    "config/config.yaml",
    "requirements.txt",
    "setup.py",
    "app.py",
    ".gitignore",
    "README.md",
]

if __name__ == "__main__":
    for directory in DIRECTORIES:
        Path(directory).mkdir(parents=True, exist_ok=True)
    created = 0
    for file in FILES:
        path = Path(file)
        if not path.exists():
            path.touch()
            created += 1
    print(f"Project structure ready ({created} new files created).")
