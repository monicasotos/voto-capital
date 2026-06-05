# Voto Capital

Explores whether left/right presidential election outcomes correlate with currency depreciation, widening risk premiums, and local asset devaluation across Latin America.

## Setup

Requires Python 3.13 and [`uv`](https://docs.astral.sh/uv/).

```bash
uv sync
```

## Dashboard

```bash
uv run streamlit run dashboards/etf_explorer.py
```

Open http://localhost:8501. Stop with `Ctrl+C`.

## Tests

```bash
uv run pytest
```

## Data

Raw source files live in `data/raw/`. To convert them to the clean format used by the dashboard:

```bash
uv run python -m voto_capital.transforms.etf
uv run python -m voto_capital.transforms.fx
uv run python -m voto_capital.transforms.bonds
```

Clean files are committed to `data/` so you don't need to run conversions unless you add new raw data.
