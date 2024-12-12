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

    messages: Annotated[List[AnyMessage], add_messages]
    library: str = field(default="")

@dataclass(kw_only=True)
class AgentState(InputState):
    """State of the retieval graph / agent."""

    steps: list[str] = field(default_factory=list)
    """A list of steps in the research plan."""
    documents: Annotated[list[Document], reduce_docs] = field(default_factory=list)
    """Populated by the retriever. This is a list of documents that the agent can reference."""
    code: Annotated[list[tuple[str, ...]], reduce_codes] = field(default_factory=list)
    """Populated by the retriever. This is a list of code blocks that the agent can reference."""
    answer: str = field(default="")
    """Final answer. Useful for evaluations"""
    query: str = field(default="")
    """Original Query user sent it."""
    current_step: str = field(default="")
    """The current step in the research plan"""












