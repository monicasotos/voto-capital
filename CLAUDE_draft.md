# voto-capital

## What this is

A data analysis dashboard to examine — and critically evaluate — the claim that:

> Left-wing presidential victories cause currency depreciation, widening risk premiums, and devaluation of local assets; right-wing victories produce the opposite.

The original claim was made using only Chile as evidence. This project extends the analysis to multiple countries (Colombia, Brazil, Mexico, Chile, USA) using ETF prices as a proxy for local equity markets, and will incorporate FX rates, sovereign debt, and country risk data as they become available.

The goal is not to confirm the claim but to stress-test it across geographies and election cycles.

---

## Tech stack

- Python 3.13
- `uv` for package management (not pip)
- `pandas` for data manipulation
- `Streamlit` + `Plotly` for the dashboard
- `pytest` (TDD only — tests are written before or alongside implementation)

---

## Project structure

```
voto-capital/
├── src/voto_capital/
│   ├── loaders/         ← one module per data type (prices.py, fx.py, bonds.py, ...)
│   └── transforms/      ← pure functions: normalization, windowing, correlations, ...
├── dashboards/
│   └── app.py           ← Streamlit entry point
├── tests/
│   ├── loaders/
│   ├── transforms/
│   └── scripts/
├── scripts/
│   └── normalize_data.py  ← run once to clean raw CSVs
└── data/
    ├── mapping_countries_files.json
    └── raw/             ← canonical CSVs (after normalize_data.py has been run)
```

`loaders/` grows as new data sources are added. `transforms/` holds stateless functions that operate on DataFrames — no I/O, easy to test.

---

## Data

### Raw files

Located in `data/raw/`. Named by ticker: `etf_{ticker}.csv`.

Current files: `etf_colo.csv`, `etf_ech.csv`, `etf_eww.csv`, `etf_ewz.csv`, `etf_qqq.csv`, `etf_vti.csv`

### Canonical CSV format

After running `scripts/normalize_data.py`, all files share this schema:

| Column   | Format                       |
|----------|------------------------------|
| Date     | `YYYY-MM-DD`                 |
| Price    | float (period decimal)       |
| Open     | float                        |
| High     | float                        |
| Low      | float                        |
| Vol.     | string (e.g. `1.25M`, `96K`)|
| Change % | string (e.g. `0.19%`)       |

### Country mapping

`data/mapping_countries_files.json` maps country keys to lists of raw files:

```json
{
  "USA": ["raw/etf_vti.csv", "raw/etf_qqq.csv"],
  "COLOMBIA": ["raw/etf_colo.csv"],
  ...
}
```

A country can have multiple ETFs (e.g. USA has VTI for broad market and QQQ as tech benchmark).

### Adding new data

When adding a new data type (e.g. FX rates):
1. Add raw files to `data/raw/` with a clear prefix: `fx_{country}.csv`
2. Add entries to `mapping_countries_files.json`
3. Update `scripts/normalize_data.py` to handle the new format if needed
4. Add `src/voto_capital/loaders/fx.py`

---

## Setup

```bash
uv sync --dev
```

---

## Running things

```bash
uv run pytest                                    # run tests
uv run streamlit run dashboards/app.py           # launch dashboard
uv run python scripts/normalize_data.py          # normalize raw data (run once)
```

---

## Coding rules

- No comments unless the *why* is non-obvious. Never explain what the code does.
- Small changes. If something touches more than a few files, explain the plan first and wait for approval.
- Always show planned changes before executing them.
- No premature abstractions.
- TDD — tests before implementation, always.
- Tests use real data files — no mocks for the data layer.
- Never use pip, always uv.
