import os

project_structure = [
    "src/components",
    "src/pipeline",
    "src/utils",
    "config",
    "logs",
    ".github/workflows"
]

files = [
    "src/components/data_ingestion.py",
    "src/components/data_validation.py",
    "src/components/data_transformation.py",
    "src/components/model_trainer.py",
    "src/components/prediction.py",
    "src/pipeline/train_pipeline.py",
    "src/pipeline/predict_pipeline.py",
    "src/utils/logger.py",
    "config/config.yaml",
    "requirements.txt",
    "setup.py",
    "app.py",
    ".gitignore",
    "README.md"
]

for folder in project_structure:
    os.makedirs(folder, exist_ok=True)

for file in files:
    with open(file, "w") as f:
        pass

print("✅ Project structure created successfully!")
