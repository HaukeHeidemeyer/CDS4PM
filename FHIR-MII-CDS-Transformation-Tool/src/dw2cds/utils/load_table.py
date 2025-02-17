from __future__ import annotations

import pandas as pd


def load_table_as_df(location: str, dtype: dict = {}):
    df = pd.read_csv(
        filepath_or_buffer=location,
        delimiter="|",
        dtype=dtype,
        encoding="utf",
    )
    return df
