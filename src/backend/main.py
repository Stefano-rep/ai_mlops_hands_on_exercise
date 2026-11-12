"""FastAPI entry point."""

from typing import Annotated, Literal

from fastapi import Depends, FastAPI, Query

from .data import NUMERIC, clean, correlations, dataset, distribution, filtered

app = FastAPI(title="AI/MLops API", root_path="/api")


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/message")
def message() -> dict[str, str]:
    return {"message": "Hello from FastAPI!"}


def selection(search: str = Query('', max_length=200), income: str = '', sex: str = ''):
    return filtered(search, income, sex)


Selection = Annotated[object, Depends(selection)]


@app.get('/metadata')
def metadata():
    frame = dataset()
    return {
        'columns': frame.columns.tolist(),
        'numeric': NUMERIC,
        'categorical': [col for col in frame.columns if col not in NUMERIC],
        'total': len(frame),
        'filters': {col: sorted(frame[col].dropna().unique().tolist()) for col in ['income', 'sex']},
    }


@app.get('/records')
def records(frame: Selection, page: int = Query(1, ge=1), page_size: int = Query(25, ge=1, le=100)):
    offset = (page - 1) * page_size
    return {'columns': frame.columns.tolist(), 'rows': clean(frame.iloc[offset:offset + page_size]),
            'total': len(frame), 'page': page, 'page_size': page_size}


@app.get('/analysis/distribution')
def analyze_distribution(frame: Selection, column: str = 'age', bins: int = Query(20, ge=2, le=100), weighted: bool = False):
    return {'total': len(frame), **distribution(frame, column, bins, weighted)}


@app.get('/analysis/education')
def education(frame: Selection):
    mapping = frame[['education_num', 'education']].drop_duplicates().sort_values('education_num')
    percentages = frame['education_num'].value_counts(normalize=True).sort_index() * 100
    return {'total': len(frame), 'labels': [f'{row.education_num} - {row.education}' for row in mapping.itertuples()],
            'values': percentages.tolist(), 'summary': {}}


@app.get('/analysis/correlations')
def analyze_correlations(frame: Selection, method: Literal['pearson', 'cramers_v'] = 'pearson'):
    return {'total': len(frame), **correlations(frame, method)}
