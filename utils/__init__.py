import streamlit as st
from streamlit.components.v1 import iframe


@st.dialog("Relevant videos", width="large")
def video_dialog(results: list[str]):
    for url in results:
        iframe(
            src=url.removesuffix("?autoplay=1"),
            width=560,
            height=315,
            scrolling=True
        )


@st.dialog("Relevant Links", width="large")
def search_dialog(results):
    for id in results:
        st.write(f"""
            {id["url"]}\n
            {id["content"]}
            """)
