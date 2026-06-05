import json
from pathlib import Path

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from voto_capital.loaders.elections import load_elections
from voto_capital.loaders.etf import load_etf

DATA_DIR = Path(__file__).parents[1] / "data"
MAPPING_FILE = DATA_DIR / "mapping_countries_files.json"
ELECTIONS_FILE = DATA_DIR / "elections.json"
FX_FILE = DATA_DIR / "fx_changes.csv"
BOND_FILE = DATA_DIR / "bond_yield_changes.csv"

# Argentina bond data is 9-year; all others are 10-year
BOND_TENOR_LABEL = {col: "9Y" if col == "ARGENTINA" else "10Y" for col in ["ARGENTINA", "BRAZIL", "CHILE", "COLOMBIA", "MEXICO", "USA"]}


def _wing_color(wing: str) -> str:
    if "left" in wing:
        return "#e05252"
    if "right" in wing:
        return "#5282e0"
    return "#aaaaaa"


@st.cache_data
def _load_all_etfs() -> dict[str, pd.DataFrame]:
    mapping: dict[str, list[str]] = json.loads(MAPPING_FILE.read_text())
    result = {}
    for country, files in mapping.items():
        for filename in files:
            ticker = filename.replace("etf_", "").replace(".csv", "").upper()
            label = f"{country} ({ticker})"
            result[label] = load_etf(DATA_DIR / filename)
    return result


@st.cache_data
def _load_wide(path: Path) -> pd.DataFrame:
    return pd.read_csv(path, index_col="date", parse_dates=True).sort_index()


_ANNOTATION_Y_STEPS = [0.97, 0.85, 0.73, 0.61]


def _add_election_markers(
    fig: go.Figure,
    selected_countries: set[str],
    start: pd.Timestamp,
    end: pd.Timestamp,
) -> None:
    idx = 0
    for election in load_elections(ELECTIONS_FILE):
        if election["country"] not in selected_countries:
            continue
        color = _wing_color(election.get("wing", ""))
        for round_date, round_label in [
            (election["first_round"], "R1"),
            (election["second_round"], "R2"),
        ]:
            if round_date is None or not (start <= round_date <= end):
                continue
            fig.add_shape(
                type="line",
                x0=round_date, x1=round_date,
                y0=0, y1=1,
                yref="paper",
                line=dict(color=color, width=1.5, dash="dash"),
            )
            fig.add_annotation(
                x=round_date,
                y=_ANNOTATION_Y_STEPS[idx % len(_ANNOTATION_Y_STEPS)],
                yref="paper",
                text=f"{election['country']} {round_label}",
                showarrow=False,
                font=dict(size=10, color=color),
                bgcolor="rgba(0,0,0,0.5)",
                borderpad=2,
                xanchor="left",
            )
            idx += 1


def _build_chart(
    series_dict: dict[str, pd.Series],
    selected: list[str],
    selected_countries: set[str],
    start: pd.Timestamp,
    end: pd.Timestamp,
    view: str,
    yaxis_range: list | None,
    yaxis_title_cumulative: str,
    yaxis_title_daily: str,
    height: int = 500,
) -> go.Figure:
    fig = go.Figure()
    for label in selected:
        series = series_dict[label].loc[start:end].dropna()
        if series.empty:
            continue
        if view == "Cumulative return":
            y = ((1 + series).cumprod() * 100).values
        else:
            y = (series * 100).values
        fig.add_trace(go.Scatter(x=series.index, y=y, name=label, mode="lines", connectgaps=False))

    _add_election_markers(fig, selected_countries, start, end)
    fig.update_layout(
        xaxis_title="Date",
        yaxis_title=yaxis_title_cumulative if view == "Cumulative return" else yaxis_title_daily,
        yaxis={} if view == "Cumulative return" else {"range": yaxis_range},
        hovermode="x unified",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="left", x=0),
        height=height,
    )
    return fig


# ---------------------------------------------------------------------------
st.set_page_config(page_title="Voto Capital", layout="wide")
st.title("Voto Capital")

all_etfs = _load_all_etfs()
fx = _load_wide(FX_FILE)
bonds = _load_wide(BOND_FILE)

# --- shared controls ---
all_dates = pd.concat(
    [df.index.to_series() for df in all_etfs.values()]
).drop_duplicates().sort_values()
global_min = all_dates.min().date()
global_max = all_dates.max().date()

ctrl_left, ctrl_mid, ctrl_right = st.columns([2, 2, 2])
with ctrl_left:
    start_date = st.date_input("From", value=global_min, min_value=global_min, max_value=global_max)
with ctrl_mid:
    end_date = st.date_input("To", value=global_max, min_value=global_min, max_value=global_max)
with ctrl_right:
    daily_view = st.toggle("Daily change %", value=False)
    view = "Daily change %" if daily_view else "Cumulative return"

if start_date >= end_date:
    st.warning("'From' must be before 'To'.")
    st.stop()

start, end = pd.Timestamp(start_date), pd.Timestamp(end_date)

# --- ETF section ---
st.subheader("Equity markets (ETF)")
etf_selected = st.multiselect("Select ETFs", options=sorted(all_etfs.keys()), default=sorted(all_etfs.keys()), key="etf_select")

etf_series = {}
for label in etf_selected:
    col = "price" if view == "Cumulative return" else "change_pct"
    s = all_etfs[label][col]
    if view == "Cumulative return":
        first = s.dropna().iloc[0]
        etf_series[label] = s / first - 1  # convert to fractional return so cumprod works uniformly
    else:
        etf_series[label] = s

etf_fig = go.Figure()
for label in etf_selected:
    df = all_etfs[label]
    series = df.loc[start:end, "price" if view == "Cumulative return" else "change_pct"]
    if series.empty:
        continue
    if view == "Cumulative return":
        y = (series / series.dropna().iloc[0] * 100).values
    else:
        y = (series * 100).values
    etf_fig.add_trace(go.Scatter(x=series.index, y=y, name=label, mode="lines", connectgaps=False))

_add_election_markers(etf_fig, {l.split(" (")[0] for l in etf_selected}, start, end)
etf_fig.update_layout(
    xaxis_title="Date",
    yaxis_title="Cumulative return (base = 100)" if view == "Cumulative return" else "Daily change (%)",
    yaxis={} if view == "Cumulative return" else {"range": [-12, 12]},
    hovermode="x unified",
    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="left", x=0),
    height=500,
)
if view == "Daily change %":
    st.caption("Y-axis clamped to ±12%.")
st.plotly_chart(etf_fig, use_container_width=True)

# --- FX section ---
st.divider()
st.subheader("Currency vs USD")
st.caption("Positive = local currency appreciated vs dollar. Negative = depreciated.")

fx_selected = st.multiselect("Select countries", options=sorted(fx.columns.tolist()), default=sorted(fx.columns.tolist()), key="fx_select")
fx_series = {c: fx[c] for c in fx_selected}

fx_fig = _build_chart(
    fx_series, fx_selected, set(fx_selected),
    start, end, view,
    yaxis_range=[-8, 8],
    yaxis_title_cumulative="Cumulative currency return (base = 100)",
    yaxis_title_daily="Daily change (%)",
)
if view == "Daily change %":
    st.caption("Y-axis clamped to ±8%.")
st.plotly_chart(fx_fig, use_container_width=True)

# --- Bond yield section ---
st.divider()
st.subheader("Government bond yields")
st.caption("10-year local-currency bond yield change. Argentina: 9-year. Positive = yield rose (risk premium widened).")

bond_options = sorted(bonds.columns.tolist())
bond_selected = st.multiselect(
    "Select countries",
    options=bond_options,
    default=bond_options,
    key="bond_select",
)
bond_series = {f"{c} ({BOND_TENOR_LABEL[c]})": bonds[c] for c in bond_selected}

bond_fig = _build_chart(
    bond_series, list(bond_series.keys()), set(bond_selected),
    start, end, view,
    yaxis_range=[-5, 5],
    yaxis_title_cumulative="Cumulative yield change (base = 100)",
    yaxis_title_daily="Daily yield change (%)",
)
if view == "Daily change %":
    st.caption("Y-axis clamped to ±5%. Brazil has very limited data (23 rows).")
st.plotly_chart(bond_fig, use_container_width=True)
