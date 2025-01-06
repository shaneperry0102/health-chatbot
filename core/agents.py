from langgraph.graph.message import MessagesState
from langgraph.graph import StateGraph, START, END
from langgraph.prebuilt import ToolNode

from langchain_core.messages import SystemMessage
from langchain_core.language_models.chat_models import BaseChatModel


class Agent:
    def __init__(self, model: BaseChatModel, tools, system=""):
        self.system = system
        self.model = model.bind_tools(tools=tools, tool_choice="auto")

        builder = StateGraph(MessagesState)
        builder.add_node("llm", self.call_model)
        builder.add_node("tools", ToolNode(tools))
        builder.add_edge(START, "llm")
        builder.add_conditional_edges("llm", self.should_continue)
        builder.add_edge("tools", "llm")
        self.graph = builder.compile()

    def should_continue(self, state: MessagesState):
        last_message = state["messages"][-1]

        if last_message.tool_calls:
            return "tools"
        else:
            return END

    def call_model(self, state: MessagesState):
        messages = state["messages"]
        if self.system:
            messages = [SystemMessage(content=self.system)] + messages
        response = self.model.invoke(messages)

        return {"messages": [response]}
