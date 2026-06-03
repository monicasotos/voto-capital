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

WING_COLOR = {"left": "#e05252", "right": "#5282e0"}


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
def _load_fx() -> pd.DataFrame:
    df = pd.read_csv(FX_FILE, index_col="date", parse_dates=True)
    return df.sort_index()


def _add_election_markers(
    fig: go.Figure,
    selected_countries: set[str],
    start: pd.Timestamp,
    end: pd.Timestamp,
) -> None:
    for election in load_elections(ELECTIONS_FILE):
        if election["country"] not in selected_countries:
            continue
        color = WING_COLOR.get(election["wing"], "#aaaaaa")
        for round_date, round_label in [
            (election["first_round"], "R1"),
            (election["second_round"], "R2"),
        ]:
            if round_date is None or not (start <= round_date <= end):
                continue
            fig.add_vline(
                x=round_date.timestamp() * 1000,
                line_dash="dash",
                line_color=color,
                line_width=1.5,
                annotation_text=f"{election['country']} {round_label}",
                annotation_position="top",
                annotation_font_size=10,
                annotation_font_color=color,
            )


st.set_page_config(page_title="Voto Capital", layout="wide")
st.title("Voto Capital")

all_etfs = _load_all_etfs()
fx = _load_fx()

# --- shared controls ---
all_dates = pd.concat(
    [df.index.to_series() for df in all_etfs.values()]
).drop_duplicates().sort_values()
min_date, max_date = all_dates.min().date(), all_dates.max().date()

ctrl_left, ctrl_right = st.columns([2, 3])
with ctrl_left:
    date_range = st.date_input(
        "Date range",
        value=(min_date, max_date),
        min_value=min_date,
        max_value=max_date,
    )
with ctrl_right:
    daily_view = st.toggle("Daily change %", value=False)
    view = "Daily change %" if daily_view else "Cumulative return"

if len(date_range) != 2:
    st.stop()

start, end = pd.Timestamp(date_range[0]), pd.Timestamp(date_range[1])

# --- ETF section ---
st.subheader("Equity markets (ETF)")

etf_selected = st.multiselect(
    "Select ETFs",
    options=sorted(all_etfs.keys()),
    default=sorted(all_etfs.keys()),
    key="etf_select",
)

etf_fig = go.Figure()

for label in etf_selected:
    df = all_etfs[label]
    if view == "Cumulative return":
        series = df.loc[start:end, "price"]
        if series.empty:
            continue
        y = (series / series.dropna().iloc[0] * 100).values
    else:
        series = df.loc[start:end, "change_pct"]
        if series.empty:
            continue
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

fx_selected = st.multiselect(
    "Select countries",
    options=sorted(fx.columns.tolist()),
    default=sorted(fx.columns.tolist()),
    key="fx_select",
)

fx_fig = go.Figure()

for country in fx_selected:
    series = fx.loc[start:end, country].dropna()
    if series.empty:
        continue
    if view == "Cumulative return":
        y = ((1 + series).cumprod() * 100).values
    else:
        y = (series * 100).values

    fx_fig.add_trace(go.Scatter(x=series.index, y=y, name=country, mode="lines", connectgaps=False))

_add_election_markers(fx_fig, set(fx_selected), start, end)

fx_fig.update_layout(
    xaxis_title="Date",
    yaxis_title="Cumulative currency return (base = 100)" if view == "Cumulative return" else "Daily change (%)",
    yaxis={} if view == "Cumulative return" else {"range": [-8, 8]},
    hovermode="x unified",
    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="left", x=0),
    height=500,
)

if view == "Daily change %":
    st.caption("Y-axis clamped to ±8%. Max single-day COP move in dataset: +3.39% (2022-05-30), -6.23% (2020-03-09).")
st.plotly_chart(fx_fig, use_container_width=True)
