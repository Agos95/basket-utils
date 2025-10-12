import streamlit as st

from pdf_parsing import parse_pdf

st.set_page_config(layout="wide")

file = st.file_uploader("Upload PDF", type="pdf")
if file:
    df = parse_pdf(file)
    teams = df["Home"].unique()
    index = None
    for i, team in enumerate(teams):
        if "arcella" in team.lower():
            index = i

    team = st.selectbox("Filter Teams", options=teams, index=index, key="team_filter")
    if team:
        df = df.loc[(df["Home"] == team) | (df["Away"] == team)]
    st.dataframe(df, hide_index=True)

    st.download_button("Download", data=df.to_csv(index=None), file_name="calendar.csv")
