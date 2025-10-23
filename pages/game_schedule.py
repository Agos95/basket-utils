import os
from datetime import date, datetime, timedelta

import pandas as pd
import streamlit as st

_URL = os.getenv("GOOGLE_SHEET_URL")
_COLUMNS = ["home", "away", "date", "time", "court", "address", "category"]


@st.cache_data
def _get_df():
    df = pd.read_csv(_URL)
    df["date"] = pd.to_datetime(df["date"], format="%d/%m/%Y")
    return df


@st.cache_data
def _filter_df(
    df: pd.DataFrame,
    start: date | None = None,
    end: date | None = None,
    col: str = "date",
):
    idx = pd.Series([True for _ in range(len(df))])
    if start:
        idx = idx & (df["date"].dt.date >= start)
    if end:
        idx = idx & (df["date"].dt.date < end)
    df = df.loc[idx].reset_index(drop=True)
    df = df.set_index([[i + 1 for i in range(len(df))]])
    return df


@st.fragment
def date_input():
    dates = st.date_input(
        "Date",
        value=(datetime.now(), datetime.now() + timedelta(days=7)),
    )

    if dates and len(dates) == 2:
        if (
            st.session_state.get("start", None) != dates[0]
            or st.session_state.get("end", None) != dates[1]
        ):
            st.session_state["start"] = dates[0]
            st.session_state["end"] = dates[1]
            st.rerun()


st.title("Game Schedule")

df = _get_df()

# put date selection in fragment,
# otherwise reload is triggered even when we do not select both dates
date_input()
st.dataframe(
    _filter_df(
        df,
        st.session_state.get("start", None),
        st.session_state.get("end", None),
    )
)
