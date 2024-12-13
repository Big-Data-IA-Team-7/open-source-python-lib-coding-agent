from typing import Dict, List, TypedDict
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langgraph.graph import StateGraph, END
from pydantic import BaseModel, Field

class CodeGenerationState(TypedDict):
    """State for the code generation graph."""
    requirement: str
    code: str
    documentation: str
    implementation_details: str
    edge_cases: List[str]

class CodeOutput(BaseModel):
    """Schema for code generation output."""
    code: str = Field(description="The generated code")
    documentation: str = Field(description="Documentation for the code")
    implementation_details: str = Field(description="Detailed explanation of the implementation")
    edge_cases: List[str] = Field(description="List of potential edge cases to consider")

class CodeGenerationGraph:
    def __init__(self, openai_api_key: str):
        """Initialize the code generation graph with API key."""
        self.llm = ChatOpenAI(
            temperature=0,
            model="gpt-4-turbo-preview",
            api_key=openai_api_key
        )
        self.workflow = self._create_workflow()

    def _analyze_requirements(self, state: CodeGenerationState) -> CodeGenerationState:
        """Analyze requirements and generate initial code."""
        prompt = ChatPromptTemplate.from_messages([
            ("system", "You are an expert programmer. Analyze the requirements and generate well-documented code."),
            ("user", "{requirement}")
        ])
        
        chain = prompt | self.llm.with_structured_output(CodeOutput) | self._process_output
        
        result = chain.invoke({"requirement": state["requirement"]})
        return {**state, **result}

    def _process_output(self, output: CodeOutput) -> Dict:
        """Process the structured output from the LLM."""
        return {
            "code": output.code,
            "documentation": output.documentation,
            "implementation_details": output.implementation_details,
            "edge_cases": output.edge_cases
        }

    def _create_workflow(self) -> StateGraph:
        """Create the LangGraph workflow for code generation."""
        # Initialize the graph
        workflow = StateGraph(CodeGenerationState)
        
        # Add nodes
        workflow.add_node("analyze_requirements", self._analyze_requirements)
        
        # Define edges
        workflow.set_entry_point("analyze_requirements")
        workflow.add_edge("analyze_requirements", END)
        
        return workflow.compile()

    def process_requirement(self, requirement: str) -> Dict:
        """Process a programming requirement through the graph."""
        initial_state = {
            "requirement": requirement,
            "code": "",
            "documentation": "",
            "implementation_details": "",
            "edge_cases": []
        }
        
        # Execute the graph
        result = self.workflow.invoke(initial_state)
        
        return {
            "code": result["code"],
            "documentation": result["documentation"],
            "implementation_details": result["implementation_details"],
            "edge_cases": result["edge_cases"]
        }