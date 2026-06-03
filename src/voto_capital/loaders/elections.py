import json
import pandas as pd
from pathlib import Path


def load_elections(path: Path | str) -> list[dict]:
    raw = json.loads(Path(path).read_text())
    result = []
    for entry in raw:
        if not entry.get("first_round"):
            continue
        result.append({
            **entry,
            "first_round": pd.Timestamp(entry["first_round"]),
            "second_round": pd.Timestamp(entry["second_round"]) if entry.get("second_round") else None,
        })
    return result
