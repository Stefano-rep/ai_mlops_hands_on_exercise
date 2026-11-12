"""Read the cleaned census and reproduce the notebook calculations."""

import json
import os
from functools import lru_cache
from pathlib import Path

import numpy as np
import pandas as pd
from fastapi import HTTPException
from scipy.stats import chi2_contingency

NUMERIC = ['age', 'fnlwgt', 'education_num', 'capital_gain', 'capital_loss', 'hours_per_week']
DATA_PATH = Path(os.getenv('CENSUS_DATA_PATH', Path(__file__).resolve().parents[2] / 'datasets' / 'census_income_cleaned.csv'))


@lru_cache(maxsize=1)
def dataset():
    try:
        return pd.read_csv(DATA_PATH)
    except (OSError, ValueError) as exc:
        raise HTTPException(503, 'Cleaned census dataset is unavailable or invalid.') from exc


def filtered(search='', income='', sex=''):
    frame = dataset()
    for column, value in [('income', income), ('sex', sex)]:
        if value:
            frame = frame[frame[column] == value]
    if search.strip():
        matches = frame.astype(str).apply(lambda col: col.str.contains(search.strip(), case=False, regex=False)).any(axis=1)
        frame = frame[matches]
    return frame


def clean(frame):
    """Convert missing and undefined numeric results into JSON nulls."""
    return json.loads(frame.to_json(orient='split'))['data']


def distribution(frame, column, bins, weighted):
    if column not in frame.columns:
        raise HTTPException(422, 'Unknown column')
    if frame.empty:
        return {'labels': [], 'values': [], 'summary': {}}
    if column in NUMERIC:
        weights = frame['fnlwgt'].to_numpy() if weighted else None
        counts, edges = np.histogram(frame[column], bins=bins, weights=weights)
        total = counts.sum()
        values = counts / total * 100 if total else np.zeros_like(counts, dtype=float)
        labels = [f'{left:.2f} – {right:.2f}' for left, right in zip(edges[:-1], edges[1:])]
        summary = json.loads(frame[column].describe().to_json())
        return {'labels': labels, 'values': values.tolist(), 'edges': edges.tolist(), 'summary': summary}
    counts = frame[column].fillna('Missing').value_counts()
    return {'labels': counts.index.tolist(), 'values': counts.tolist(), 'summary': {}}


def correlations(frame, method):
    if method == 'pearson':
        matrix = frame[NUMERIC].corr(method='pearson')
    else:
        columns = frame.select_dtypes(include=['object', 'string']).columns
        matrix = pd.DataFrame(np.nan, index=columns, columns=columns)
        for left in columns:
            for right in columns:
                table = pd.crosstab(frame[left].fillna('Missing'), frame[right].fillna('Missing'))
                # Preserve the notebook's exclusion of binary variables.
                if min(table.shape) > 2:
                    chi2 = chi2_contingency(table)[0]
                    matrix.loc[left, right] = np.sqrt(chi2 / (table.to_numpy().sum() * (min(table.shape) - 1)))
    return {'columns': matrix.columns.tolist(), 'values': clean(matrix)}
