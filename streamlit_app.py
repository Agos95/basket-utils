import streamlit as st

st.set_page_config(
    page_title="Arcella Basket Utilities", page_icon="assets/icon.svg", layout="wide"
)
st.logo(
    "assets/logo.svg",
    icon_image="assets/icon.svg",
    link="https://www.pallacanestroarcella.com/",
    size="large",
)

pages = [
    st.Page("pages/home.py", title="Home"),
    st.Page("pages/fip_calendar.py", title="Fip Calendar"),
]

pg = st.navigation(pages=pages, position="top")
pg.run()
