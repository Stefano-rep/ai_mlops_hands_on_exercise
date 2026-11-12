# Task 1 report: Data Analysis

> **Guidance.** Copy this file to `reports/task[N].md` at the end of each task and fill it in as you go.
>
> - Replace every [placeholder]; delete every Guidance block before you tag.
> - Keep it short: one to three pages. Prefer tables and figures to prose.
> - Write in English, in your own words. Explain *why*; do not paste code the reader can open in the repository.
> - Every section ends with an **Evidence** line: a notebook cell, file path, test, commit or screenshot. A claim with no evidence counts as not done.
>
> What to focus on in sections 3 and 4:
>
> | Task | Focus on |
> | --- | --- |
> | 1. Exploratory data analysis | Data quality checks and fixes; main findings, each with a number; what each finding means for later tasks |
> | 2. App deployment | Architecture; image and configuration choices; how the app gets its data; deployment trade-offs |
> | 3. AI agent | Evaluation protocol and baseline; model choice; agent tools and prompt rules; example dialogues including one failure; deployment |
> | 4. Presentation | Overall architecture; decision log across all tasks; what you would change for production |

| Field | Value |
| --- | --- |
| Student | Stefano Benaglia |
| Dataset | census_income |
| Task | 1 |
| Tag / commit | task1  |
| How to run | run the notebooks in /notebook |
| Timebox | 4.5 h , finished |

## 1. Summary

3 notebooks where built:
- data_wrangling.ipynb
- distribution_analysis.ipynb
- target_analysis.ipynb

Also a file named data_loader.py that loads the dirty and clean datasets when needed.

data_wrangling performs the cleaning of the chosen dataset, removing duplicates, formatting columns names and values to remove spaces and "-". The clean dataset create is saved in the folder /datasets and used for correlation and target analysis.

correlation_analysis performs the analysis of correlation between numeric and string features, the results found weak correlations between capital_gain and education, it also found there are moderate correlations between:
- race e native_country
- relationship e marital_status
- occupation e workclass

target_analysis searches for correlations between features and target and also anomalies in the target. It was discovered that:
- Record with an income lesser or equal 50k are more than 3 times the record with more than 50k of income
- a correlation between income and education
- a correlation between income and occupation
- a correlation between gender and income

With a multivariate analysis it was also found that the income of people with the same degree varies with age.

The most important limitation in this phase was time.

## 2. Goal and success criteria

> **Guidance.** State what the task asked for and how you decide whether you succeeded. Fix the criteria before you look at results.

**Goal.** analyse the dataset to find correlations, anomalies and format the dataset for a correct data analysis

| Criterion | How it is measured | Target | Result |
| --- | --- | --- | --- |
| data cleaning | dataset quality | clean dataset | clean dataset |
| find correaltions | pearson and caramer's V  | correlations | found correlations|

**Evidence:** The dataset after wrangling is easier to manipulate and analyse, Correlations between features have been found and more importantly correlations between features and target

## 3. Approach and key decisions

| # | Finding | Decision | Alternative considered | Where in the code |
| --- | --- | --- | --- | --- |
| D1 | spaces before column names | remove | load ignoring spaces | data_wrangling.ipynb |
| D2 | "?" in column values | subsitute with NaN | removing rows | data_wrangling.ipynb |
| D3 | "-" in column names | subsitution with "_" | removing "-" | data_wrangling.ipynb |
| D4 |  duplicate rows | removing rows | - | data_wrangling.ipynb |
| D5 |  different values in income | equal formatting | - | data_wrangling.ipynb |


## 7. Next steps

| Priority | Next step | Why | Effort |
| --- | --- | --- | --- |
| 1 | Create API Applicaction | - | M |




## Checklist

- [X] Task tag pushed and named in the table at the top
- [ ] Runs from a fresh clone with the commands above
- [X] No secrets, API keys or large data files committed
- [X] Every section has an Evidence line
- [X] Every figure has a caption with a number
- [X] `AI_LOG.md` up to date
