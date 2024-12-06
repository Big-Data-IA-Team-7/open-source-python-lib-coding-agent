"""Define the configurable parameters for the agent."""

from __future__ import annotations

from dataclasses import dataclass, field

from langgraph_graphs.langgraph_agents.configuration import BaseConfiguration
from langgraph_graphs.langgraph_agents.code_retrieval_graph import prompts


@dataclass(kw_only=True)
class AgentConfiguration(BaseConfiguration):
    """The configuration for the agent."""

    # models

    query_model: str = field(
        default="openai/gpt-4o-mini",
        metadata={
            "description": "The language model used for processing and refining queries. Should be in the form: provider/model-name."
        },
    )

    response_model: str = field(
        default="openai/gpt-4o-mini",
        metadata={
            "description": "The language model used for generating responses. Should be in the form: provider/model-name."
        },
    )

    research_plan_system_prompt: str = field(
        default=prompts.RESEARCH_PLAN_SYSTEM_PROMPT,
        metadata={
            "description": "The system prompt used for generating a research plan based on the user's question."
        },
    )

    sql_code_check_prompt: str = field(
        default=prompts.SQL_GENERATE_QUESTION_PROMPT,
        metadata={
            "description": "The system prompt used for rechecking the SQL queries generated based on the user's question."
        },
    )

    generate_queries_system_prompt: str = field(
        default=prompts.GENERATE_QUERIES_SYSTEM_PROMPT,
        metadata={
            "description": "The system prompt used by the researcher to generate queries based on a step in the research plan."
        },
    )

    response_system_prompt: str = field(
        default=prompts.RESPONSE_SYSTEM_PROMPT,
        metadata={"description": "The system prompt used for generating responses."},
    )

    eh_response_system_prompt: str = field(
        default=prompts.EH_RESPONSE_SYSTEM_PROMPT,
        metadata={"description": "The system prompt used for generating responses to the errors."},
    )