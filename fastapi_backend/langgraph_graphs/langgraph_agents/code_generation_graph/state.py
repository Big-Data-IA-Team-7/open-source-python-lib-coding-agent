from dataclasses import dataclass, field
from typing import Annotated, List
from langchain_core.documents import Document
from langchain_core.messages import AnyMessage
from langgraph.graph import add_messages
from fastapi_backend.langgraph_graphs.langgraph_agents.utils import reduce_docs, reduce_codes

@dataclass(kw_only=True)
class InputState:
    """Represents the input state for the agent.
    
    This class defines the structure of the input state, which includes
    the messages exchanged between the user and the agent. It serves as
    a restricted version of the full State, providing a narrower interface
    to the outside world compared to what is maintained internally.
    """

    messages: Annotated[List[AnyMessage], add_messages]
    library: str = field(default="")

@dataclass(kw_only=True)
class AgentState(InputState):
    """State of the retrieval graph / agent."""

    research_steps: list[str] = field(default_factory=list)
    """A list of steps in the research plan."""
    app_steps: list[str] = field(default_factory=list)
    """A list of steps in the app plan."""
    documents: Annotated[list[Document], reduce_docs] = field(default_factory=list)
    """Populated by the retriever. This is a list of documents that the agent can reference."""
    library_code: Annotated[list[tuple[str, ...]], reduce_codes] = field(default_factory=list)
    """Populated by the retriever. This is a list of code blocks that the agent can reference."""
    answer: str = field(default="")
    """Final answer. Useful for evaluations."""
    query: str = field(default="")
    """To store the user query."""
    frontend: str = field(default="")
    """To store the frontend code provided by code generated agent."""
    backend: str = field(default="")
    """To store the backend code provided by code generated agent."""
    feedback_content: str = field(default="")
    """Feedback provided. This is the feedback provided by the LLM for the generated code."""
    code_evaluated: bool = field(default=False)
    """Boolean flag indicating whether the code has been evaluated."""
    requirements: str = field(default="")
    """Populated by the requirements .txt generation agent. This contains the requirements txt required."""
    readme_content: str = field(default="")
    """Populated by the readme generation agent. This contains the readme content to push to GitHub."""
