import pandas as pd
from pathlib import Path


def is_raw_etf_file(path: Path | str) -> bool:
    return "ETF" in Path(path).name


def raw_to_clean_filename(path: Path | str) -> str:
    ticker = Path(path).stem.split()[0].lower()
    return f"etf_{ticker}.csv"


def read_raw_etf(path: Path | str) -> pd.DataFrame:
    df = pd.read_csv(path, encoding="utf-8-sig")
    df["Date"] = pd.to_datetime(df["Date"], format="%m/%d/%Y")
    df = df.set_index("Date").sort_index()
    df["Price"] = df["Price"].astype(float)
    return df


if __name__ == "__main__":
    import sys

    raw_dir = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("data/raw")
    out_dir = Path(sys.argv[2]) if len(sys.argv) > 2 else Path("data")

    for raw_file in sorted(raw_dir.glob("*.csv")):
        if not is_raw_etf_file(raw_file):
            continue
        out_name = raw_to_clean_filename(raw_file)
        df = read_raw_etf(raw_file)
        df.to_csv(out_dir / out_name)
        print(f"{raw_file.name} → {out_name} ({len(df)} rows)")
