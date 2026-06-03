import pandas as pd
from pathlib import Path


def load_etf(path: Path | str) -> pd.DataFrame:
    df = pd.read_csv(
        path,
        parse_dates=["Date"],
        dtype={"Price": float, "Change %": str, "Vol.": str},
    )
    df["change_pct"] = (
        df["Change %"].str.rstrip("%").astype(float) / 100.0
    )
    df = df.rename(columns={"Date": "date", "Price": "price"})
    df = df.set_index("date")[["price", "change_pct"]]
    df = df.sort_index()
    return df
