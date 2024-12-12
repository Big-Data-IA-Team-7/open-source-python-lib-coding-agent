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
APP_RESEARCH_PLAN_SYSTEM_PROMPT = (
    hub.pull("code-generation-research-plan-prompt")
    .messages[0]
    .prompt.template
)
SQL_GENERATE_QUESTION_PROMPT = (
    hub.pull("generate-question-for-sql-prompt")
    .messages[0]
    .prompt.template
)
BUILD_APP_RESPONSE_PROMPT = (
    hub.pull("build-app-response-prompt").messages[0].prompt.template
)
RESPONSE_SYSTEM_PROMPT = (
    hub.pull("qa-documentation-response-prompt").messages[0].prompt.template
)
EH_RESPONSE_SYSTEM_PROMPT = (
    hub.pull("eh-response-prompt").messages[0].prompt.template
)
CODE_GENERATION_SYSTEM_PROMPT = (
    hub.pull("code-generation-system-prompt").messages[0].prompt.template
)
CODE_EVALUATION_SYSTEM_PROMPT = (
    hub.pull("code-evaluation-system-prompt").messages[0].prompt.template
)
REQUIREMENTS_TXT_GENERATION_SYSTEM_PROMPT = (
    hub.pull("requirements-txt-generation-system-prompt").messages[0].prompt.template
)
README_MD_GENERATION_SYSTEM_PROMPT = (
    hub.pull("readme-md-generation-system-prompt").messages[0].prompt.template
)
JUDGE_EVALUATION_SYSTEM_PROMPT = (
    hub.pull("judge-evaluation-system-prompt").messages[0].prompt.template
)
REGENERATE_CODE_SYSTEM_PROMPT = (
    hub.pull("regenerate-code-system-prompt").messages[0].prompt.template
)