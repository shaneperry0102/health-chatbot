import streamlit as st

from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage, AIMessage, ToolMessage

import ast

from core import HealthAgent, YouTubeAgent, TavilySearch, YoutubeSearch
from utils import youtube_dialog, search_dialog


#
# Page Configuration
#
st.set_page_config(
    page_title="Healthcare Assistant",
    page_icon=":stethoscope:",
    layout="centered",
    menu_items={
        "Report a bug": "https://github.com/shaneperry0102/health-chatbot/issues/new?title=New Bug&body=Here is a bug detail.",
        "About": "## This is an *extremely* cool healthcare chatbot!"
    },
    initial_sidebar_state="collapsed"
)

model = ChatGroq(
    model="llama3-70b-8192",
    temperature=1,
    max_tokens=None,
    timeout=None,
    max_retries=2,
    streaming=True,
    api_key=st.secrets["GROQ_API_KEY"],
    # other params...
)
tools = [TavilySearch]

system_prompt = """You are a smart healthcare assistant. You should first check if the questions are related to healthcare. \
If not, do not answer, just refuse it, like "Sorry, I can't answer that question.". \
Use the search engine to look up information if needed. \
You are allowed to make multiple calls (either together or in sequence). \
Only look up information when you are sure of what you want. \
If you need to look up some information before asking a follow up question, you are allowed to do that!
"""


@st.cache_resource
def create_health_agent():
    health_agent = HealthAgent(model, tools, system=system_prompt)
    yt_agent = YouTubeAgent(model, system=system_prompt)
    return health_agent


@st.cache_resource
def create_yt_agent():
    yt_agent = YouTubeAgent(model, system=system_prompt)
    return yt_agent


@st.cache_data
def create_graph_image():
    return create_health_agent().graph.get_graph().draw_mermaid_png()


@st.cache_data
def create_yt_graph_image():
    return create_yt_agent().graph.get_graph().draw_mermaid_png()


@st.cache_resource
def initialize_session_state():
    """Initialize chat history"""
    if "chat_history" not in st.session_state:
        st.session_state["messages"] = []
        st.session_state["tool_text_list"] = []
        st.session_state["chat_history"] = []


initialize_session_state()

#
# Sidebar
#
with st.sidebar:
    st.subheader(
        "This is the LangGraph workflow visualization of this application rendered in real-time.")
    st.image(create_graph_image())
    st.image(create_yt_graph_image())
    "[View the source code](https://github.com/shaneperry0102/health-chatbot/blob/main/app.py)"
    "[![Open in GitHub Codespaces](https://github.com/codespaces/badge.svg)](https://codespaces.new/shaneperry0102/health-chatbot?quickstart=1)"

#
# Title
#
st.title(":stethoscope: Healthcare Assistant")

messages = st.container()

#
# Display chat messages from history on app rerun
#
for message in st.session_state["chat_history"]:
    if message["role"] == "user":
        messages.chat_message("user").write(message["content"]["text"])
    elif message["role"] == "assistant":
        assistant_chat = messages.chat_message("assistant")
        if isinstance(message["content"], list):
            for part in message["content"]:
                if part["type"] == "text":
                    assistant_chat.markdown(part["text"])
                elif part["type"] == "search":
                    results = ast.literal_eval(part["text"])
                    if len(results):
                        videoButton = assistant_chat.button(
                            "Youtube videos", key=part["text"])
                        if videoButton:
                            youtube_dialog(results)
                elif part["type"] == "tavily":
                    results = ast.literal_eval(part["text"])
                    if len(results):
                        videoButton = assistant_chat.button(
                            "Relevant links", key=results)
                        if videoButton:
                            search_dialog(results)
        else:
            assistant_chat.markdown(message["content"])

#
# React to user input
#
if user_prompt := st.chat_input(placeholder="Message Here"):
    # Display user message in chat message container
    messages.chat_message("user").write(user_prompt)
    # Add user message to chat history
    st.session_state["messages"].append(HumanMessage(content=user_prompt))
    st.session_state["chat_history"].append(
        {"role": "user", "content": {"type": "text", "text": user_prompt}})

    thread = {"configurable": {"thread_id": "4"}}
    aimessages = ""
    graph = create_health_agent().graph
    yt_graph = create_yt_agent().graph

    st.session_state["tool_text_list"] = []

    searchResults = None

    assistant_chat = messages.chat_message("assistant")
    for event in graph.stream(
        input={"messages": st.session_state["messages"]},
        config=thread,
        stream_mode="values"
    ):
        # print(f"Event: {event}")
        message = event["messages"][-1]
        if isinstance(message, AIMessage) and message.content:
            # print(f"Message: {str(message.content)}")
            aimessages += str(message.content)
            st.session_state["tool_text_list"].append(
                {"type": "text", "text": message.content})
            assistant_chat.markdown(message.content)
        elif isinstance(message, ToolMessage) and message.name == TavilySearch.name:
            searchResults = message.content

    if searchResults:
        st.session_state["tool_text_list"].append(
            {"type": "tavily", "text": searchResults})
        results = ast.literal_eval(searchResults)
        if len(searchResults):
            videoButton = assistant_chat.button(
                "Relevant links", key=searchResults)
            if videoButton:
                search_dialog(searchResults)

    for event in yt_graph.stream(
        input={"messages": st.session_state["messages"]},
        config=thread,
        stream_mode="values"
    ):
        # print(f"Event YouTube: {event}")
        message = event["messages"][-1]
        if isinstance(message, ToolMessage):
            if message.name == YoutubeSearch.name:
                st.session_state["tool_text_list"].append(
                    {"type": "search", "text": message.content})
                # print(
                #     f"content: {message.content} ---- type: {type(message.content)}")
                results = ast.literal_eval(message.content)
                if len(results):
                    videoButton = assistant_chat.button(
                        "Youtube videos", key=message.content)
                    if videoButton:
                        youtube_dialog(results)

    st.session_state["messages"].append(AIMessage(content=aimessages))
    st.session_state["chat_history"].append(
        {"role": "assistant", "content": st.session_state["tool_text_list"]})
