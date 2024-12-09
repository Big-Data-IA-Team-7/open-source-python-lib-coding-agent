from dataclasses import dataclass, field
from typing import Annotated, List
from langchain_core.documents import Document
from langchain_core.messages import AnyMessage
from langgraph.graph import add_messages
from langgraph_graphs.langgraph_agents.utils import reduce_docs, reduce_codes

@dataclass(kw_only=True)
class InputState:
    """Represents the input state for the agent.
    
    This class defines the structure of the input state, which includes
    the messages exchanged between the user and the agent. It serves as
    a restricted version of the full State, providing a narrower interface
    to the outside world compared to what is maintained internally.
    """

    messages: Annotated[List[AnyMessage], add_messages]

@dataclass(kw_only=True)
class AgentState(InputState):
    """State of the retrieval graph / agent."""

    steps: list[str] = field(default_factory=list)
    """A list of steps in the research plan."""
    documents: Annotated[list[Document], reduce_docs] = field(default_factory=list)
    """Populated by the retriever. This is a list of documents that the agent can reference."""
    code: Annotated[list[tuple[str, ...]], reduce_codes] = field(default_factory=list)
    """Populated by the retriever. This is a list of code blocks that the agent can reference."""
    answer: str = field(default="")
    """Final answer. Useful for evaluations."""
    query: str = field(default="")
    """To store the user query."""
    code_generated: str = field(default="")
    """Populated by the code generation agent. This contains the code generated."""
    requirements: str = field(default="")
    """Populated by the requirements .txt generation agent. This contains the requirements txt required."""
    readme_content: str = field(default="")
    """Populated by the readme generation agent. This contains the readme content to push to GitHub."""
    feedback_content: str = field(default="")
    """Feedback provided. This is the feedback provided by the LLM for the generated code."""
    feedback_value: int = field(default=0)  # Changed to a default integer value
    """Threshold for the loop. This is the threshold calculated by the LLM."""
