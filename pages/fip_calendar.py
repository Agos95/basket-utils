import pandas as pd
import streamlit as st

import pdf_parsing

_ST_TEAM_MAPPING_KEY = "team_rename"
_DEFAULT_TEAM = "arcella"

parse_pdf = st.cache_data(pdf_parsing.parse_pdf)


@st.cache_data
def _get_default_team(teams: list[str]) -> int:
    for i, team in enumerate(teams):
        if _DEFAULT_TEAM in team.lower():
            break
    return i


@st.cache_data
def _filter_df(df: pd.DataFrame, team: str) -> pd.DataFrame:
    df = df.loc[(df["Home"] == team) | (df["Away"] == team)].reset_index(drop=True)
    df = df.set_index([[i + 1 for i in range(len(df))]])
    return df


@st.cache_data()
def _replace_team(df: pd.DataFrame, mapping: dict[str, str | None]) -> str:
    def _rename(x):
        new_name = mapping.get(x, None)
        if new_name:
            return new_name
        return x

    df["Home"] = df["Home"].apply(_rename)
    df["Away"] = df["Away"].apply(_rename)

    return df


st.title("FIP Calendar Parser")

team_selector_col, file_upload_col = st.columns([0.5, 0.5])

with file_upload_col:
    file = st.file_uploader("Upload PDF", type="pdf")

if file:
    df = parse_pdf(file)
    teams = sorted(df["Home"].unique())
    if _ST_TEAM_MAPPING_KEY not in st.session_state:
        st.session_state[_ST_TEAM_MAPPING_KEY] = {t: "" for t in teams}

    with team_selector_col:
        team = st.selectbox(
            "Filter Teams",
            options=teams,
            index=_get_default_team(teams),
        )

    table_col, rename_col = st.columns([0.7, 0.3], gap="large")

    with table_col:
        if team:
            df = _filter_df(df, team)
        rename = st.session_state.get(_ST_TEAM_MAPPING_KEY, None)
        if rename is not None:
            df = _replace_team(df, mapping=rename)

        st.markdown("#### Games")
        st.dataframe(df, hide_index=False)

        st.download_button(
            "Download",
            data=df.to_csv(index=None),
            file_name="calendar.csv",
            icon=":material/download:",
        )

    with rename_col:
        rename_df = st.session_state[_ST_TEAM_MAPPING_KEY]

        st.markdown("#### Rename Teams")
        rename_df = st.data_editor(
            rename_df, column_config={0: "Team", 1: "Rename"}, disabled=[0]
        )
        if rename_df != st.session_state[_ST_TEAM_MAPPING_KEY]:
            st.session_state[_ST_TEAM_MAPPING_KEY] = rename_df
            st.rerun()
