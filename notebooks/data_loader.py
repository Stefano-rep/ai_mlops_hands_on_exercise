from pathlib import Path
import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parent.parent

def load_dataset():
    path = PROJECT_ROOT / "datasets" / "census_income.csv"
    return pd.read_csv(path)

def load_dataset_cleaned():
    path = PROJECT_ROOT / "datasets" / "census_income_cleaned.csv"
    return pd.read_csv(path)