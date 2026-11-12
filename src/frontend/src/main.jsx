import React, { useEffect, useState } from 'react';
import { createRoot } from 'react-dom/client';
import './style.css';
import { distributionNotes, correlationNotes } from './notebookNotes';

function NotebookNote({ text }) {
  if (!text) return null;
  return <aside className="notebook-note" aria-label="Analysis observation">
    <h3>Analysis observation</h3><p>{text}</p>
    <small>This observation describes the full dataset, rather than the currently selected filters or weighting.</small>
  </aside>;
}

function useApi(path) {
  const [state, setState] = useState({ path: null, data: null, error: '', loading: true });
  useEffect(() => {
    const controller = new AbortController();
    setState({ path, data: null, error: '', loading: true });
    fetch(`/api/${path}`, { signal: controller.signal })
      .then(async response => {
        if (!response.ok) {
          const body = await response.json();
          throw new Error(typeof body.detail === 'string' ? body.detail : `Request failed (${response.status})`);
        }
        return response.json();
      })
      .then(data => {
        if (!controller.signal.aborted) setState({ path, data, error: '', loading: false });
      })
      .catch(error => {
        if (!controller.signal.aborted) setState({ path, data: null, error: error.message, loading: false });
      });
    return () => controller.abort();
  }, [path]);
  // Effects run after rendering: never expose another endpoint's payload.
  return state.path === path ? state : { data: null, error: '', loading: true };
}

function Bars({ data }) {
  const max = Math.max(...data.values, 1);
  return <div className="bars">{data.labels.map((label, i) => <div className="bar-row" key={label}>
    <span>{label}</span><div className="track"><div className="bar" style={{ width: `${data.values[i] / max * 100}%` }} /></div>
    <strong>{Number(data.values[i]).toLocaleString(undefined, { maximumFractionDigits: 2 })}</strong>
  </div>)}</div>;
}

function Matrix({ data, method }) {
  return <div className="table-wrap"><table><caption>{method === 'pearson' ? 'Pearson correlation (−1 to 1)' : "Cramér’s V (0 to 1). — indicates an undefined value or a variable with at most two categories, as in the notebook."}</caption>
    <thead><tr><th>Feature</th>{data.columns.map(col => <th key={col}>{col}</th>)}</tr></thead>
    <tbody>{data.values.map((row, i) => <tr key={data.columns[i]}><th>{data.columns[i]}</th>{row.map((value, j) => <td key={j} style={{ background: value === null ? 'transparent' : `rgba(${value < 0 ? '214, 90, 100' : '45, 150, 190'}, ${Math.abs(value) * .8})` }}>{value === null ? '—' : value.toFixed(2)}</td>)}</tr>)}</tbody>
  </table></div>;
}

function Explorer({ meta }) {
  const [tab, setTab] = useState('records');
  const [search, setSearch] = useState('');
  const [draft, setDraft] = useState('');
  const [income, setIncome] = useState('');
  const [sex, setSex] = useState('');
  const [page, setPage] = useState(1);
  const [pageSize, setPageSize] = useState(25);
  const [column, setColumn] = useState('age');
  const [bins, setBins] = useState(20);
  const [weighted, setWeighted] = useState(false);
  const [method, setMethod] = useState('pearson');
  const [education, setEducation] = useState(false);
  const numeric = meta.numeric.includes(column);
  const query = new URLSearchParams({ search, income, sex });
  let endpoint = `records?${query}&page=${page}&page_size=${pageSize}`;
  if (tab === 'distribution') endpoint = `analysis/${education ? 'education' : 'distribution'}?${query}&column=${column}&bins=${bins}&weighted=${weighted}`;
  if (tab === 'correlations') endpoint = `analysis/correlations?${query}&method=${method}`;
  const { data, error, loading } = useApi(endpoint);
  const updateFilter = (setter, value) => { setter(value); setPage(1); };
  return <>
    <header><p className="eyebrow">Census income · {meta.total.toLocaleString()} records</p><h1>Explore the census</h1><p>Browse the cleaned data and explore the distributions and correlations from the analysis notebooks.</p></header>
    <section className="controls" aria-label="Dataset filters">
      <form onSubmit={event => { event.preventDefault(); updateFilter(setSearch, draft); }}><label>Search all columns<input value={draft} onChange={event => setDraft(event.target.value)} maxLength={200} /></label><button>Search</button></form>
      {['income', 'sex'].map(key => <label key={key}>{key}<select value={key === 'income' ? income : sex} onChange={event => updateFilter(key === 'income' ? setIncome : setSex, event.target.value)}><option value="">All</option>{meta.filters[key].map(value => <option key={value}>{value}</option>)}</select></label>)}
      <button onClick={() => { setSearch(''); setDraft(''); setIncome(''); setSex(''); setPage(1); }}>Reset filters</button>
    </section>
    <nav aria-label="Explorer views">{[['records', 'Data'], ['distribution', 'Distributions'], ['correlations', 'Correlations']].map(([key, label]) => <button aria-pressed={tab === key} key={key} onClick={() => setTab(key)}>{label}</button>)}</nav>
    {tab === 'distribution' && <section className="controls">
      <label>Analysis<select value={education ? 'education' : 'feature'} onChange={e => setEducation(e.target.value === 'education')}><option value="feature">Feature distribution</option><option value="education">Education levels (%)</option></select></label>
      {!education && <><label>Feature<select value={column} onChange={e => setColumn(e.target.value)}>{meta.columns.filter(col => col !== 'fnlwgt').map(col => <option key={col}>{col}</option>)}</select></label>
      {numeric && <><label>Histogram bins<select value={bins} onChange={e => setBins(Number(e.target.value))}>{[10, 20, 30, 50].map(n => <option key={n}>{n}</option>)}</select></label><label className="check"><input type="checkbox" checked={weighted} onChange={e => setWeighted(e.target.checked)} />Weight by fnlwgt</label></>}</>}
    </section>}
    {tab === 'correlations' && <label>Method<select value={method} onChange={e => setMethod(e.target.value)}><option value="pearson">Pearson · numeric features</option><option value="cramers_v">Cramér’s V · categorical features</option></select></label>}
    <section aria-live="polite" aria-busy={loading}>
      {loading && <p>Loading…</p>}{error && <p role="alert" className="error">{error}</p>}
      {data && <><p>{data.total.toLocaleString()} matching records. Analyses use all matching records.</p>
      {data.total === 0 ? <p>No records match these filters.</p> : <>
      {tab === 'records' && <><div className="table-wrap"><table><thead><tr>{data.columns.map(col => <th key={col}>{col}</th>)}</tr></thead><tbody>{data.rows.map((row, i) => <tr key={i}>{row.map((cell, j) => <td key={j}>{cell ?? '—'}</td>)}</tr>)}</tbody></table></div>
      <div className="controls"><button disabled={page <= 1} onClick={() => setPage(page - 1)}>Previous</button><span>Page {page} of {Math.ceil(data.total / pageSize)}</span><button disabled={page * pageSize >= data.total} onClick={() => setPage(page + 1)}>Next</button><label>Rows per page<select value={pageSize} onChange={e => updateFilter(setPageSize, Number(e.target.value))}>{[25, 50, 100].map(n => <option key={n}>{n}</option>)}</select></label></div></>}
      {tab === 'distribution' && <><h2>{education ? 'Education levels' : column}</h2><p>{education || numeric ? `Percentage (%)${!education && weighted ? ' · weighted by fnlwgt' : ''}` : 'Record count'}</p><Bars data={data} /><NotebookNote text={distributionNotes[education ? 'education_num' : column]} />{Object.keys(data.summary).length > 0 && <><h2>Descriptive statistics (unweighted)</h2><dl>{Object.entries(data.summary).map(([key, value]) => <div key={key}><dt>{key}</dt><dd>{value == null ? '—' : value.toLocaleString(undefined, { maximumFractionDigits: 2 })}</dd></div>)}</dl></>}</>}
      {tab === 'correlations' && <><Matrix data={data} method={method} /><NotebookNote text={correlationNotes[method]} /></>}
      </>}</>}
    </section><footer><a href="/api/docs">API documentation</a></footer>
  </>;
}

function App() {
  const { data, error, loading } = useApi('metadata');
  return <main>{loading ? <p>Loading dataset…</p> : error ? <p role="alert" className="error">{error}</p> : <Explorer meta={data} />}</main>;
}
createRoot(document.getElementById('root')).render(<App />);
