"""Inference tools using the complete fitted training pipeline."""

import os
from functools import lru_cache
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
from langchain_core.tools import tool
from threadpoolctl import threadpool_limits

DEFAULT_MODEL = Path(__file__).resolve().parents[2] / 'artifacts' / 'mlp_pipeline.joblib'


@lru_cache(maxsize=1)
def load_model():
    path = Path(os.getenv('ML_MODEL_PATH', str(DEFAULT_MODEL)))
    if not path.is_file():
        raise FileNotFoundError(f'MLP artifact not found: {path}. Run the training script first.')
    return joblib.load(path)


@tool
def input_schema() -> dict:
    """List the exact required MLP input features, types and known categories."""
    model = load_model()
    preprocessing = model.named_steps['preprocessing']
    numeric = list(preprocessing.transformers_[0][2])
    categorical = list(preprocessing.transformers_[1][2])
    encoder = preprocessing.named_transformers_['categorical'].named_steps['encoder']
    return {
        'required_features': list(model.feature_names_in_),
        'numeric_features': numeric,
        'categorical_features': dict(zip(categorical, [values.tolist() for values in encoder.categories_])),
        'target': {'0': '<=50K', '1': '>50K'},
        'note': 'Supply every feature, excluding income and high_income. Encoded binary features must be 0 or 1.',
    }


@tool
def predict_income(record: dict) -> dict:
    """Predict census income using the fitted MLP. Supply a complete feature record from input_schema."""
    model = load_model()
    schema = input_schema.invoke({})
    required = set(schema['required_features'])
    missing = sorted(required - record.keys())
    extra = sorted(record.keys() - required)
    if missing or extra:
        return {'error': 'Feature mismatch', 'missing_features': missing, 'unexpected_features': extra}
    for name in schema['numeric_features']:
        value = record[name]
        if not isinstance(value, (int, float)) or not np.isfinite(value):
            return {'error': f'{name} must be a finite number.'}
        if name.startswith(('race_', 'sex_', 'occupation_')) and value not in (0, 1):
            return {'error': f'{name} must be 0 or 1.'}
    for name, categories in schema['categorical_features'].items():
        if not isinstance(record[name], str) or record[name] not in categories:
            return {'error': f'Unknown category for {name}. Use input_schema for allowed values.'}
    frame = pd.DataFrame([record], columns=schema['required_features'])
    with threadpool_limits(limits=2):
        prediction = int(model.predict(frame)[0])
        probabilities = model.predict_proba(frame)[0]
    return {
        'prediction': prediction,
        'income': '>50K' if prediction else '<=50K',
        'probabilities': {('>50K' if int(label) else '<=50K'): float(value)
                          for label, value in zip(model.classes_, probabilities)},
        'model': 'MLPClassifier',
    }
