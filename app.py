import streamlit as st

from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage, AIMessage, ToolMessage

import ast
import os

from core.agents import HealthAgent, VideoAgent
from core.tools import TavilySearch, VideoSearch
from utils import video_dialog, search_dialog


# Page configuration
st.set_page_config(
    page_title="Healthcare Assistant",
    page_icon=":stethoscope:",
    layout="centered",
    menu_items={
        "Report a bug": "https://github.com/shaneperry0102/health-chatbot/issues/new?title=New Bug&body=Here is a bug detail.",
        "About": "## This is an *extremely* cool healthcare chatbot!"
    },
    initial_sidebar_state="auto"
)


# Sidebar
with st.sidebar:
    bar = st.container()

    st.title(":stethoscope: Healthcare Assistant")

    st.write('This chatbot is created using the LLM model from Groq.')
    if 'GROQ_API_KEY' in st.secrets:
        st.success('API key already provided!', icon='✅')
        groq_api = st.secrets['GROQ_API_KEY']
    else:
        groq_api = st.text_input(
            'Enter Groq API token:', type='password')
        if not (groq_api.startswith('gsk_') and len(groq_api) == 56):
            st.warning('Please enter your credentials!', icon='⚠️')
        else:
            st.success('Proceed to entering your prompt message!', icon='👉')
    os.environ['GROQ_API_KEY'] = groq_api

    st.subheader('Models and parameters')
    selected_model = st.sidebar.selectbox(
        'Choose a Groq model', ['llama3-70b-8192'], key='selected_model')
    temperature = st.sidebar.slider(
        'temperature', min_value=0.01, max_value=2.0, value=1.0, step=0.01)

    st.write(
        "[View the source code](https://github.com/shaneperry0102/health-chatbot/blob/main/app.py)")
    st.write("[![Open in GitHub Codespaces](https://github.com/codespaces/badge.svg)](https://codespaces.new/shaneperry0102/health-chatbot?quickstart=1)")


def init_chat_history():
    """Initialize chat history"""
    st.session_state["messages"] = []
    st.session_state["chat_history"] = []


if "chat_history" not in st.session_state:
    init_chat_history()

bar.button('Clear Chat History', on_click=init_chat_history)


tools = []

system_prompt = """You are a smart healthcare assistant. You should first check if the questions are related to healthcare. \
If not, do not answer, just refuse it, like "Sorry, I can't answer that question.". \
Use the search engine to look up information if needed. \
You are allowed to make multiple calls (either together or in sequence). \
Only look up information when you are sure of what you want. \
If you need to look up some information before asking a follow up question, you are allowed to do that!
"""


@st.cache_resource
def create_health_agent():
    model = ChatGroq(
        model=selected_model,
        temperature=temperature,
        max_tokens=None,
        timeout=None,
        max_retries=2,
        streaming=True
    )
    health_agent = HealthAgent(model, tools, system=system_prompt)
    return health_agent


@st.cache_resource
def create_video_agent():
    model = ChatGroq(
        model=selected_model,
        temperature=temperature,
        max_tokens=None,
        timeout=None,
        max_retries=2,
        streaming=True
    )
    yt_agent = VideoAgent(model, system=system_prompt)
    return yt_agent


messages = st.container()

# Display chat messages from history on app rerun
for message in st.session_state["chat_history"]:
    if message["role"] == "user":
        messages.chat_message("user").write(message["content"]["text"])
    elif message["role"] == "assistant":
        assistant_chat = messages.chat_message("assistant")
        for part in message["content"]:
            if part["type"] == "text":
                assistant_chat.markdown(part["text"])
            elif part["type"] == "youtube":
                if assistant_chat.button("Videos", key=part["list"]):
                    video_dialog(part["list"])
            elif part["type"] == "search":
                if assistant_chat.button("Sources", key=part["list"]):
                    search_dialog(part["list"])


# React to user input
if user_prompt := st.chat_input(placeholder="Message Here", disabled=not groq_api):
    # Display user message in chat message container
    messages.chat_message("user").write(user_prompt)
    # Add user message to chat history
    st.session_state["messages"].append(HumanMessage(content=user_prompt))
    st.session_state["chat_history"].append(
        {"role": "user", "content": {"type": "text", "text": user_prompt}})

    thread = {"configurable": {"thread_id": "4"}}
    aimessages = ""
    health_graph = create_health_agent().graph
    yt_graph = create_video_agent().graph

    tool_text_list = []
    searchResults = None

    with messages.chat_message("assistant"):
        with st.spinner("Thinking..."):
            for event in health_graph.stream(
                input={"messages": st.session_state["messages"]},
                config=thread,
                stream_mode="values"
            ):
                message = event["messages"][-1]
                if isinstance(message, AIMessage) and message.content:
                    aimessages += str(message.content)
                    tool_text_list.append(
                        {"type": "text", "text": message.content})
                    st.markdown(message.content)
                elif isinstance(message, ToolMessage) and message.name == TavilySearch.name:
                    searchResults = ast.literal_eval(message.content)

            if searchResults and len(searchResults):
                tool_text_list.append(
                    {"type": "search", "list": searchResults})
                if st.button("Sources", key=searchResults):
                    search_dialog(searchResults)

            for event in yt_graph.stream(
                input={"messages": st.session_state["messages"]},
                config=thread,
                stream_mode="values"
            ):
                message = event["messages"][-1]
                if isinstance(message, ToolMessage) and message.name == VideoSearch.name:
                    results = ast.literal_eval(message.content)
                    if len(results):
                        tool_text_list.append(
                            {"type": "youtube", "list": results})
                        if st.button("Videos", key=results):
                            video_dialog(results)

    st.session_state["messages"].append(AIMessage(content=aimessages))
    st.session_state["chat_history"].append(
        {"role": "assistant", "content": tool_text_list})
