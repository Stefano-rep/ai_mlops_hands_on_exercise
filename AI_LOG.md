| Time | Purpose | Kept |
|------|---------|------|
| 2026-11-12 | Execute PROMPT.md: scaffold FastAPI, React, Nginx and Docker Compose | Application boilerplate, dependency locks, container configuration and startup instructions |
| 2026-11-12 | Execute updated PROMPT.md: browse cleaned census and expose existing notebook analyses | Filtered and paginated API, selectable distributions and correlation matrices, React explorer and read-only dataset mount |
| 2026-11-12 | Fix frontend crashes when switching analysis views | Associate fetched state with its endpoint and discard responses from cancelled requests |
| 2026-11-12 | Hide fnlwgt from distribution features | Removed fnlwgt from the frontend feature selector; retained weighting support |
| 2026-11-12 | Display existing notebook observations in English | Added attributed observations below distributions and correlations; new observations await user confirmation |
| 2026-11-12 | Apply user-approved analysis observations | Added five categorical distribution comments and corrected the capital gain/loss interpretation |
| 2026-11-12 | Restyle dashboard using the Bootstrap dashboard example as reference | Left navigation, warm cream and terracotta palette, responsive layout, revised tables and charts |
| 2026-11-12 | Train Logistic Regression and MLPClassifier as explicitly requested | Training-only preprocessing pipelines, stratified 60/20/20 split, duplicate/conflicting-label exclusions, validation F1 selection and final test comparison |
| 2026-11-12 | Compare numeric-only training against the original pipelines on identical training/validation partitions | Numeric-only validation F1 decreased for both models; train.py left unchanged and test set not evaluated |
| 2026-11-12 | Compare training without fnlwgt on identical training/validation splits | Logistic Regression accuracy slightly increased but best overall validation accuracy decreased; train.py unchanged and test set not evaluated |
| 2026-11-12 | Evaluate original and no-fnlwgt MLP on the test set as requested | Compared test accuracy, F1, recall and ROC-AUC on 9,033 records; train.py unchanged |
| 2026-11-12 | Package the original MLP with joblib | Saved the fitted preprocessing/classifier pipeline to artifacts/mlp_pipeline.joblib, added reproducible export to train.py and verified reloaded predictions |
| 2026-11-12 | Create CLI LangGraph agent and Compose deployment | Offline mock tool-calling graph, configurable OpenAI provider with fake key, validated MLP inference tool, read-only artifact mount, usage examples and offline integration tests |
| 2026-11-12 | Replace local agent terminal with a Tkinter interface | Default desktop chat, provider selector, JSON/example loading, schema and reset buttons, background inference; desktop smoke test passed, CLI retained for Docker |
| 2026-11-12 | Document application build and startup in the root README | Docker full-stack and CLI agent commands, local Tkinter launch, required files and artifact generation |
