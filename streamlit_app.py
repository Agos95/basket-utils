import pandas as pd
import streamlit as st

from pdf_parsing import parse_pdf

st.set_page_config(
    page_title="Arcella Basket Utilities", page_icon="assets/icon.svg", layout="wide"
)
st.logo("assets/icon.svg", link="https://www.pallacanestroarcella.com/")

_ST_TEAM_MAPPING_KEY = "team_rename"


@st.cache_data()
def _replace_team(x: str, mapping: dict[str, str | None]) -> str:
    new_name = mapping.get(x, None)
    if new_name:
        return new_name
    return x


st.title("Arcella Basket Utilities")


file = st.file_uploader("Upload PDF", type="pdf")
if file:
    df = parse_pdf(file)
    teams = sorted(df["Home"].unique())
    if _ST_TEAM_MAPPING_KEY not in st.session_state:
        st.session_state[_ST_TEAM_MAPPING_KEY] = {k: None for k in teams}

    index = None
    for i, team in enumerate(teams):
        if "arcella" in team.lower():
            index = i
            break
    team = st.selectbox("Filter Teams", options=teams, index=index, key="team_filter")

    table_col, rename_col = st.columns([0.7, 0.3])

    with table_col:
        if team:
            df = df.loc[(df["Home"] == team) | (df["Away"] == team)].reset_index(
                drop=True
            )
            df = df.set_index([[i + 1 for i in range(len(df))]])

        rename = st.session_state.get(_ST_TEAM_MAPPING_KEY, None)
        if rename is not None:
            # df = df.replace(to_replace=rename.keys(), value=rename.values())
            df["Home"] = df["Home"].apply(_replace_team, mapping=rename)
            df["Away"] = df["Away"].apply(_replace_team, mapping=rename)

        st.dataframe(df, hide_index=False)

        st.download_button(
            "Download", data=df.to_csv(index=None), file_name="calendar.csv"
        )

    with rename_col:
        rename_df = pd.DataFrame(
            {
                "Team": st.session_state[_ST_TEAM_MAPPING_KEY].keys(),
                "Rename": st.session_state[_ST_TEAM_MAPPING_KEY].values(),
            }
        )
        rename_df = st.data_editor(rename_df, hide_index=True, disabled=["Team"])
        # FIXME: the rerun is alway triggered, but it needs to be only if there is a modification
        rename_df = rename_df.replace(to_replace="", value=None)
        st.session_state[_ST_TEAM_MAPPING_KEY] = {
            k: v for k, v in zip(rename_df.iloc[:, 0], rename_df.iloc[:, 1])
        }
        # st.rerun()
