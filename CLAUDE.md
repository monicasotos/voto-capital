# Voto Capital

Dashboard to analyze whether left/right presidential election outcomes correlate with currency depreciation, widening
risk premiums, and local asset devaluation across Latin America.

## Commands

```bash
uv run pytest                          # run all tests
uv run pytest tests/path/to/test.py   # run a single test file

uv run python -m voto_capital.transforms.etf    # convert raw ETF files → data/
uv run python -m voto_capital.transforms.fx     # convert raw FX files → data/fx_changes.csv
uv run python -m voto_capital.transforms.bonds  # convert raw bond files → data/bond_yield_changes.csv

uv run streamlit run dashboards/etf_explorer.py
```

## Code style

- Python 3.13, `uv` for package management
- TDD only: write failing tests first, then implement
- No comments unless the *why* is non-obvious
- Prefer small, focused changes — show the plan and wait for approval before implementing anything non-trivial
- For committing, use [semantic commits](https://www.conventionalcommits.org/en/v1.0.0/. Focus on the _why_. The code
  itself tells the _what_

## Data layout

- `data/` — clean, ready-to-load files (ISO dates, no quotes, numeric types)
- `data/raw/` — raw downloads, temporary; will be removed once processed
- ETF raw files: `* ETF Stock Price History.csv` pattern
- FX raw files: `USD_* Historical Data.csv` pattern
- Bond raw files: `* Bond Yield Historical Data.csv` pattern

## Architecture

- `loaders/` — read clean files from `data/`; each loader returns a `pd.DataFrame` with a `DatetimeIndex`
- `transforms/` — convert `data/raw/` → `data/`; each module has a `__main__` block to run the conversion
- `dashboards/` — Streamlit only; no business logic here, only presentation

## Adding a new country

1. Drop raw files into `data/raw/`
2. Add the country to the relevant `RAW_FILE_MAP` in `transforms/`
3. Run the transform to produce the clean file
4. Add the ETF entry to `data/mapping_countries_files.json`
5. Add election events to `data/elections.json`
