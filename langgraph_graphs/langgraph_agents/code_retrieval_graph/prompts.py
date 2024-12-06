from langchain import hub

"""Default prompts."""

# fetch from langsmith
GENERATE_QUERIES_SYSTEM_PROMPT = (
    hub.pull("langchain-ai/chat-langchain-generate-queries-prompt")
    .messages[0]
    .prompt.template
)
RESEARCH_PLAN_SYSTEM_PROMPT = (
    hub.pull("langgraph-research-plan-prompt")
    .messages[0]
    .prompt.template
)
SQL_GENERATE_QUESTION_PROMPT = (
    hub.pull("generate-question-for-sql-prompt")
    .messages[0]
    .prompt.template
)
RESPONSE_SYSTEM_PROMPT = (
    hub.pull("qa-documentation-response-prompt").messages[0].prompt.template
)
EH_RESPONSE_SYSTEM_PROMPT = (
    hub.pull("eh-response-prompt").messages[0].prompt.template
)