import streamlit as st
from streamlit.components.v1 import iframe


@st.dialog("YouTube videos", width="large")
def youtube_dialog(results):
    for id in results:
        iframe(
            src=f"https://www.youtube.com/embed/{id}",
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
