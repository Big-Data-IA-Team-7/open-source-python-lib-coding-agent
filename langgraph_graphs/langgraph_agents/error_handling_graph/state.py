from dataclasses import dataclass, field
from typing import Annotated, List
from langchain_core.documents import Document
from langchain_core.messages import AnyMessage
from langgraph.graph import add_messages
from langgraph_graphs.langgraph_agents.utils import reduce_docs, reduce_codes

@dataclass(kw_only=True)
class InputState:
    """Represents the input state for the agent.
    
    This class defines the structure of the input state, which include
    the messages achanged between the user and the agent. It serves as
    a restrictired version of the full State, providing a narrower interface
    to the outside world compared to what is maintained internally.
    """

    task: str = field(default="")
    """This is a short description of what the user is trying to do in the code."""
    code: str = field(default="")
    """This is the code which is causing the error given by the user."""
    error: str = field(default="")
    """This is the error message that is displayed given by the user."""
    messages: Annotated[List[AnyMessage], add_messages]

@dataclass(kw_only=True)
class AgentState(InputState):
    """State of the retieval graph / agent."""

    web_search: str = field(default_factory=list)
    """The list of web search urls and information obtained from the web search agent."""
    documents: Annotated[list[Document], reduce_docs] = field(default_factory=list)
    """Populated by the retriever. This is a list of documents that the agent can reference."""
    library_code: Annotated[list[tuple[str, ...]], reduce_codes] = field(default_factory=list)
    """Populated by the retriever. This is a list of code blocks that the agent can reference."""
    answer: str = field(default="")
    """Final answer. Useful for evaluations"""
    query: str = field(default="")













