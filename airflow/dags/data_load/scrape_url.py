from bs4 import BeautifulSoup
from langchain_community.document_loaders.recursive_url_loader import RecursiveUrlLoader

def load_recursive_url(**kwargs):
    loader = RecursiveUrlLoader(
        "https://langchain-ai.github.io/langgraph/",
        max_depth=5,
        prevent_outside=True,
        extractor=lambda x: str(BeautifulSoup(x, "html.parser")),
        base_url="https://langchain-ai.github.io/langgraph/"
    )
    return loader
