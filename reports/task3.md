# Task 3 report: AI Agent

| Field | Value |
| --- | --- |
| Student | Stefano Benaglia |
| Dataset | census_income |
| Task | 3 |
| Tag / commit | task3  |
| How to run |  |
| Timebox | 2 h , finished |

## 1. Summary

I trained 2 models for classification purposes, one Logistic Regression and one MLP Classifier, using a validation set to find the best fit. The best fit appeared to be the MLP classifier so it was exported with joblib.
Then the agent was created using langraph wiht the model as tool and a mock LLM as second tool.


## 3. Approach and key decisions


| # | Finding | Decision | Alternative considered | Where in the code |
| --- | --- | --- | --- | --- |
| D1 | clean the dataset | new notebook | - | dataset_cleaning_training.ipynb |
| D2 | chose best ML model | pipeline with validation set | - | train.py |
| D3 | create AI agent | langgraph | - | agent folder |



**Evidence:** the application

## Checklist

- [ ] Task tag pushed and named in the table at the top
- [ ] Runs from a fresh clone with the commands above
- [ ] No secrets, API keys or large data files committed
- [ ] Every section has an Evidence line
- [ ] Every figure has a caption with a number
- [ ] Guidance blocks and placeholders removed
- [ ] `AI_LOG.md` up to date
