"""Compare Logistic Regression and MLP using leakage-safe 60/20/20 splits.

Run from any directory with:
    uv run python ai/ml/training/train.py
"""

import argparse
from pathlib import Path
from time import perf_counter
import warnings

import joblib
import numpy as np
import pandas as pd
import sklearn
from sklearn.compose import ColumnTransformer
from sklearn.exceptions import ConvergenceWarning
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    accuracy_score,
    balanced_accuracy_score,
    classification_report,
    confusion_matrix,
    f1_score,
    precision_score,
    recall_score,
    roc_auc_score,
)
from sklearn.model_selection import train_test_split
from sklearn.neural_network import MLPClassifier
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from threadpoolctl import threadpool_limits

DEFAULT_DATASET = Path(__file__).resolve().parents[3] / 'datasets' / 'census_income_training.csv'
SEED = 42
DEFAULT_ARTIFACT = Path(__file__).resolve().parents[3] / 'artifacts' / 'mlp_pipeline.joblib'


def load_data(path: Path) -> tuple[pd.DataFrame, pd.Series]:
    """Remove the alternative target and duplicate samples before splitting."""
    frame = pd.read_csv(path)
    if 'high_income' not in frame:
        raise ValueError('The dataset must contain the high_income target.')
    if frame['high_income'].isna().any() or set(frame['high_income'].unique()) != {0, 1}:
        raise ValueError('high_income must contain both classes 0 and 1, without missing values.')

    # income is a textual copy of high_income, so it must never enter a model.
    frame = frame.drop(columns=['income'], errors='ignore')
    features = frame.columns.drop('high_income').tolist()
    if not features:
        raise ValueError('The dataset contains no input features.')
    original_size = len(frame)
    # Exclude ambiguous feature-identical records rather than placing them in
    # different partitions or arbitrarily assigning one of their labels.
    conflicting = frame.groupby(features, dropna=False)['high_income'].transform('nunique').gt(1)
    conflicting_count = int(conflicting.sum())
    frame = frame.loc[~conflicting]
    frame = frame.drop_duplicates(subset=features).reset_index(drop=True)
    print(f'Loaded {original_size:,} records; excluded {conflicting_count:,} records with conflicting labels '
          f'and {original_size - conflicting_count - len(frame):,} duplicate samples.')
    return frame.drop(columns='high_income'), frame['high_income'].astype(int)


def split_data(features, target):
    """Reserve test first, then split the remaining 80% into 60%/20%."""
    x_remaining, x_test, y_remaining, y_test = train_test_split(
        features, target, test_size=0.20, stratify=target, random_state=SEED,
    )
    x_train, x_validation, y_train, y_validation = train_test_split(
        x_remaining, y_remaining, test_size=0.25,
        stratify=y_remaining, random_state=SEED,
    )
    return x_train, x_validation, x_test, y_train, y_validation, y_test


def build_pipeline(features, estimator):
    """Fit all learned preprocessing exclusively on the training partition."""
    numeric_columns = features.select_dtypes(include='number').columns.tolist()
    categorical_columns = features.columns.difference(numeric_columns).tolist()
    numeric = Pipeline([
        ('imputer', SimpleImputer(strategy='median')),
        ('scaler', StandardScaler()),
    ])
    categorical = Pipeline([
        ('imputer', SimpleImputer(strategy='most_frequent')),
        ('encoder', OneHotEncoder(handle_unknown='ignore', sparse_output=False)),
    ])
    preprocessing = ColumnTransformer([
        ('numeric', numeric, numeric_columns),
        ('categorical', categorical, categorical_columns),
    ])
    return Pipeline([('preprocessing', preprocessing), ('classifier', estimator)])


def evaluate(pipeline, features, target):
    predictions = pipeline.predict(features)
    probabilities = pipeline.predict_proba(features)[:, 1]
    return {
        'accuracy': accuracy_score(target, predictions),
        'balanced_accuracy': balanced_accuracy_score(target, predictions),
        'precision': precision_score(target, predictions, zero_division=0),
        'recall': recall_score(target, predictions, zero_division=0),
        'f1': f1_score(target, predictions, zero_division=0),
        'roc_auc': roc_auc_score(target, probabilities),
    }


def train(path: Path):
    features, target = load_data(path)
    x_train, x_validation, x_test, y_train, y_validation, y_test = split_data(features, target)
    print('\nStratified partitions (after deduplication):')
    for name, labels in [('Training', y_train), ('Validation', y_validation), ('Test', y_test)]:
        print(f'{name:12} {len(labels):6,} rows ({len(labels) / len(target):.1%}); high income: {labels.mean():.2%}')

    estimators = {
        'Logistic Regression': LogisticRegression(max_iter=1000, random_state=SEED),
        'MLPClassifier': MLPClassifier(
            hidden_layer_sizes=(64, 32), max_iter=200, random_state=SEED,
            early_stopping=True, validation_fraction=0.1, n_iter_no_change=15,
        ),
    }
    print('\nMLP early stopping uses only an internal subset of the training partition.')
    print('Positive class: >50K. Classification threshold: 0.5 for both models.')
    print('Selection metric: validation F1. No test data is used for fitting or selection.\n')
    fitted, validation_rows, timings = {}, {}, {}
    for name, estimator in estimators.items():
        pipeline = build_pipeline(x_train, estimator)
        start = perf_counter()
        with warnings.catch_warnings(record=True) as caught:
            warnings.simplefilter('always', ConvergenceWarning)
            pipeline.fit(x_train, y_train)
        timings[name] = perf_counter() - start
        for warning in caught:
            print(f'{name}: {warning.message}')
        fitted[name] = pipeline
        validation_rows[name] = evaluate(pipeline, x_validation, y_validation)
        print(f'{name} trained in {timings[name]:.2f}s')

    validation = pd.DataFrame.from_dict(validation_rows, orient='index')
    winner = validation['f1'].idxmax()
    print('\nVALIDATION COMPARISON')
    print(validation.to_string(float_format=lambda value: f'{value:.4f}'))
    print(f'\nSelected model: {winner} (validation F1={validation.loc[winner, "f1"]:.4f}).')
    print('A tie is resolved in favor of Logistic Regression, the simpler model.')

    # Only after selection is frozen do we evaluate either model on test data.
    test_results = pd.DataFrame.from_dict(
        {name: evaluate(model, x_test, y_test) for name, model in fitted.items()}, orient='index',
    )
    test_results['fit_seconds'] = pd.Series(timings)
    print('\nFINAL TEST COMPARISON (not used to change the selection)')
    print(test_results.to_string(float_format=lambda value: f'{value:.4f}'))
    for name, model in fitted.items():
        predictions = model.predict(x_test)
        print(f'\n{name} — test classification report')
        print(classification_report(y_test, predictions, labels=[0, 1], target_names=['<=50K', '>50K'], zero_division=0))
        print('Confusion matrix (rows=true, columns=predicted; class order: <=50K, >50K):')
        print(confusion_matrix(y_test, predictions, labels=[0, 1]))
    return fitted, winner, validation, test_results


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--dataset', type=Path, default=DEFAULT_DATASET)
    parser.add_argument('--output', type=Path, default=DEFAULT_ARTIFACT,
                        help='Destination for the fitted MLP pipeline, including preprocessing.')
    args = parser.parse_args()
    # Avoid excessive CPU thread contention on small tabular operations.
    with threadpool_limits(limits=2):
        fitted, _, _, _ = train(args.dataset)
        pipeline = fitted['MLPClassifier']
        args.output.parent.mkdir(parents=True, exist_ok=True)
        joblib.dump(pipeline, args.output, compress=3)
        restored = joblib.load(args.output)
        # Check both labels and probabilities on the same input after loading.
        sample = pd.read_csv(args.dataset, nrows=10)[pipeline.feature_names_in_]
        np.testing.assert_array_equal(pipeline.predict(sample), restored.predict(sample))
        np.testing.assert_allclose(pipeline.predict_proba(sample), restored.predict_proba(sample))
        print(f'\nMLP pipeline saved and reload verified: {args.output.resolve()}')
        print(f'scikit-learn version: {sklearn.__version__}; joblib version: {joblib.__version__}')


if __name__ == '__main__':
    main()
