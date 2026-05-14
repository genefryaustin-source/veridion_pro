from __future__ import annotations

import pandas as pd


def make_arrow_safe(df: pd.DataFrame) -> pd.DataFrame:
    """
    Convert dataframe columns into Arrow-safe types
    for Streamlit rendering.
    """

    if df is None or df.empty:
        return df

    df = df.copy()

    for col in df.columns:

        try:
            if df[col].dtype == "object":
                df[col] = df[col].fillna("").astype(str)

        except Exception:
            try:
                df[col] = df[col].astype(str)
            except Exception:
                pass

    return df