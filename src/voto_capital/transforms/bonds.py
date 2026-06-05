import pandas as pd
from pathlib import Path

RAW_FILE_MAP = {
    "ARGENTINA": "Argentina 9-Year Bond Yield Historical Data.csv",
    "BRAZIL":    "Brazil 10-Year Bond Yield Historical Data.csv",
    "CHILE":     "Chile 10-Year Bond Yield Historical Data.csv",
    "COLOMBIA":  "Colombia 10-Year Bond Yield Historical Data.csv",
    "MEXICO":    "Mexico 10-Year Bond Yield Historical Data.csv",
    "USA":       "United States 10-Year Bond Yield Historical Data.csv",
}


_MAX_DAILY_CHANGE = 0.5  # values beyond ±50% are data errors


def _parse_raw_bond(path: Path | str) -> pd.Series:
    df = pd.read_csv(path, encoding="utf-8-sig", usecols=["Date", "Change %"])
    df["Date"] = pd.to_datetime(df["Date"], format="%m/%d/%Y")
    df["change_pct"] = (
        df["Change %"].str.rstrip("%").str.replace(",", "", regex=False).astype(float) / 100.0
    )
    df.loc[df["change_pct"].abs() > _MAX_DAILY_CHANGE, "change_pct"] = float("nan")
    return df.set_index("Date").sort_index()["change_pct"]


def build_bond_changes(raw_dir: Path | str) -> pd.DataFrame:
    raw_dir = Path(raw_dir)
    df = pd.DataFrame({
        country: _parse_raw_bond(raw_dir / filename)
        for country, filename in RAW_FILE_MAP.items()
    })
    df.index.name = "date"
    return df.sort_index()


if __name__ == "__main__":
    import sys

    raw_dir = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("data/raw")
    out_path = Path(sys.argv[2]) if len(sys.argv) > 2 else Path("data/bond_yield_changes.csv")
    result = build_bond_changes(raw_dir)
    result.to_csv(out_path)
    print(f"Written {len(result)} rows to {out_path}")
