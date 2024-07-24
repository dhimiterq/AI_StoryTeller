import asyncio
from langchain_core.tools import tool
from typing import Annotated
from typing_extensions import TypedDict
from langgraph.graph.message import AnyMessage, add_messages
from langchain_core.prompts import ChatPromptTemplate
from langgraph.graph import END, StateGraph
from langgraph.prebuilt import ToolNode
from langgraph.checkpoint.aiosqlite import AsyncSqliteSaver
from langchain_chroma import Chroma
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.document_loaders import PyPDFLoader
from langchain_community.chat_models import ChatOllama
from langgraph.checkpoint.aiosqlite import AsyncSqliteSaver



local_llm = 'llama3.1:latest'

memory = AsyncSqliteSaver.from_conn_string(":memory:")


class State(TypedDict):
    # Messages have the type "list". The `add_messages` function
    # in the annotation defines how this state key should be updated
    # (in this case, it appends messages to the list, rather than overwriting them)
    messages: Annotated[list, add_messages]


llm = ChatOllama(model=local_llm, temperature=0, streaming=True)

primary_assistant_prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            "You are a useful assistant for kids. Answer user questions based on what you know, but keep the answers very short under 3-4 sentences and for an audience made of kids.",
        ),
        ("user", "{input}"),
    ]
)


def chatbot(state: State):
    return {"messages": [llm.invoke(state["messages"])]}




def create_state_graph():
    """
    Creates and returns a state graph with predefined nodes, edges, and memory checkpointing.

    Returns:
        StateGraph: A compiled state graph with nodes and edges set up.
    """
    graph_builder = StateGraph(State)

    graph_builder.add_node("chatbot", chatbot)
    graph_builder.set_entry_point("chatbot")
    graph_builder.set_finish_point("chatbot")
    graph = graph_builder.compile()
    graph = graph_builder.compile(checkpointer=memory)

    return graph

lg_agent = create_state_graph()
