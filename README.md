# Open-Source Python Library Coding Agent  

## Overview  
This project simplifies the multi-step process of working with Python libraries by leveraging LLM-powered agents. It integrates key functionalities like code generation, API references, error handling, and web search to provide a seamless, natural language-based interface for developers and learners.  

## Project Resources


### Links to the project resources:
- **Google Codelab**: [Codelab Link](https://codelabs-preview.appspot.com/?file_id=1cqfyDQM7pk3ZdG-ojvqj4_wscrx7qn1oA3dZL50mL0I#0)
- **Streamlit App** (Deployed on AWS EC2): [Streamlit Link](http://75.101.133.31:8501/)
- **Airflow** (Deployed on AWS EC2): [Airflow Link](http://75.101.133.31:8080/)
- **YouTube Demo**: [Demo Link]()

---

## Key Features

Unlock powerful capabilities that streamline your development process with intelligent repository management and interactive learning experiences.

- **Smart Repository Integration**: Upload and access any Python library instantly.
- **Interactive Learning**: Custom installation guides and tutorials.
- **Code Generation & API Mastery**: Ready-to-use code snippets.
- **Error Resolution**: Expert solutions and references.

---




## Proposal and Documentation  
For detailed information about the project's scope, objectives, and architecture, refer to the project proposal on **Google Codelab**: [Project Proposal Link](https://codelabs-preview.appspot.com/?file_id=1cqfyDQM7pk3ZdG-ojvqj4_wscrx7qn1oA3dZL50mL0I#0)

## User Flow

```mermaid
flowchart TD
    A[Start] --> B[Login Screen]
    B --> C{Authentication}
    C -->|Failure| B
    C -->|Success| D[Landing Page]
    B --> R[Registration]
    R --> B
    D --> E{Choose Python Library}
    E --> E1[Code Generation Assistant]
    E --> E2[Quick Start Guide]
    E --> E3[Error Correction]

    E1 --> F1[Provide use case]
    F1 --> F2[Generate code & explanation]
    F2 --> F3[Copy code & use it]
    F3 --> F4[User Provide feedback]
    F4 --> F1
    F4 --> E
    F4 --> Z[Exit]

    E2 --> G1[Generate quick start guide]
    G1 --> G2[Ask about functions/parameters]
    G2 --> G3[Receive response & learn]
    G3 --> G4[Publish guide to GitHub]
    G4 --> E
    G4 --> Z[Exit]

    E3 --> H1[Provide code & error message]
    H1 --> H2[Explain reason for failure]
    H2 --> H3[Generate corrected code]
    H3 --> H4[User Provide feedback]
    H4 --> H1
    H4 --> E
    H4 --> Z[Exit]

    Z[Exit]


```



## Contributors


The contributions from the team members are detailed below:

| Name                         | Contribution                                                                                  |
|------------------------------|----------------------------------------------------------------------------------------------|
| **Pragnesh Anekal**          | 33% - Github Data Parsing, Front end Streamlit, FastAPI, Langgraph Setup, Code Retreival Agent, Code Generation Agent |
| **Ram Kumar Ramasamy Pandiaraj** | 33% - Scraping Documentation, Airflow, Setting up snowflake, Code Generation Agent, Github POC, Tavilly POC, Deployment              |
| **Dipen Manoj Patel**        | 33% - Streamlit Frontend, Web Search Agent using SerpAPI,  Github MD Parsing, GitHub Push, CI/CD Pipelines   |

---

## Attestation

We attest that we haven’t used any other students' work in our assignment and abide by the policies listed in the student handbook.

