# California Water Loss Analytics

[Open the interactive dashboard](https://water-loss-analytics-rasen.streamlit.app/)

A data analysis project exploring annual water loss audits from California urban retail water systems. I use Python and SQL to examine reported losses, compare reporting coverage over time, and evaluate whether machine learning can improve on a simple next-year baseline.

Developed for **Data Analyst with SQL & Python in Google Platform — Batch 25**.

## Questions

- How much non-revenue water is reported in the selected sample?
- How do trends change when comparing the same systems across years?
- Which systems account for the largest physical loss volumes?
- Can audit information from one year help predict physical losses in the next year?

## Data and scope

Source: [California Department of Water Resources — annual water loss audits](https://data.ca.gov/@california-department-of-water-resources/ca-urban-retail-water-system-water-loss-annual-loss-audit-data).

The analysis table contains 3,507 selected calendar-year reports from 2016–2024. Reports must pass the project's cleaning rules and have either Requirements Addressed or Preliminarily Approved status. These statuses remain distinct. Results describe the selected sample, not all of California.

Volumes use acre-feet (AF). Non-revenue water includes physical losses, apparent losses, and unbilled authorized consumption; it is not equivalent to leakage alone.

## Workflow

1. `01_data_understanding.ipynb`: inspect source structure and data quality.
2. `02_data_cleaning.ipynb`: standardize fields, flag issues, and create analysis tables.
3. `03_sql_eda.ipynb`: query the data with SQLite and explore patterns.
4. `04_ml_data_preparation.ipynb`: build consecutive-year pairs and chronological splits.
5. `05_modeling_evaluation.ipynb`: compare candidates on validation and evaluate the selected model against persistence on test.
6. `app.py`: present analysis and recorded model evaluation in Streamlit.

SQL runs locally through SQLite. This project does not currently use BigQuery.

## Main findings

For the selected 2024 sample of 331 systems, aggregate non-revenue water is approximately **9.08%** of supplied water. The ten largest physical-loss volumes account for **21.42%** of total physical losses in that sample. Large volumes alone do not establish inefficiency, because system sizes differ.

### Model evaluation

The target is next-year physical loss volume. Persistence uses the previous year's physical loss as its prediction.

| Split | Target years | Observations |
|---|---|---:|
| Train | 2017–2021 | 1,850 |
| Validation | 2022–2023 | 737 |
| Test | 2024 | 307 |

Six ML candidates were compared on validation. Ridge with alpha 10 was selected using validation MAE, then refitted on train plus validation. Test data were not used to choose parameters. Negative predictions were clipped to zero under a rule defined before evaluation.

| Method | Validation MAE (AF) | Test MAE (AF) | Test RMSE (AF) |
|---|---:|---:|---:|
| Persistence | 163.18 | 142.56 | 256.58 |
| Ridge, alpha 10 | 157.12 | 149.04 | 263.30 |

Ridge improved on persistence during validation but had **4.54% higher MAE on test**. The selected ML model therefore did not outperform the baseline on the held-out period.

## Dashboard

Five pages cover the overview, trends, individual systems, ML evaluation, and methodology. The ML page reads exported CSV/JSON results; it does not train models or provide live future predictions.

Run from the repository root using a separate environment (Windows PowerShell):

```powershell
python -m venv .venv_dashboard
.\.venv_dashboard\Scripts\python.exe -m pip install -r requirements.txt
.\.venv_dashboard\Scripts\python.exe -m streamlit run app.py
```

`requirements.txt` contains dashboard dependencies only. Notebook execution also requires its analysis libraries, including scikit-learn, matplotlib, joblib, and a Jupyter kernel. Preserve the environment/version information recorded by notebook 05 when reproducing model results.

### Required dashboard files

- `app.py`, `water_loss_utils.py`, `ml_results.py`, and `requirements.txt`
- `data/processed/water_loss_analysis.csv`
- `outputs/modeling/05_model_summary.json`
- `outputs/modeling/05_test_metrics.csv`
- `outputs/modeling/05_test_predictions.csv`
- `outputs/modeling/05_validation_metrics.csv`

Cleaning tables in `outputs/tables` provide additional methodological context. Keep notebook outputs with the same data snapshot. Raw data must be present in `data/raw` to rerun the workflow from the beginning.

## Limitations

- Reporting coverage and approval statuses vary across years.
- Historical publication dates and revisions have not been verified. Model results are retrospective and do not establish operational forecasting readiness.
- Absolute-volume errors can be dominated by large systems.
- The analysis does not establish causes of losses or quantify achievable savings.
- The dashboard has been tested locally; a public deployment URL will be added after deployment succeeds.

## Author

**Raden Satrio Hibatull Rasendriyo**  
[LinkedIn](https://www.linkedin.com/in/raden-satrio) · [Email](mailto:radensatriohibatullrasendriyo@gmail.com)
