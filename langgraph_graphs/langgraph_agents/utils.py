from typing import Any, Literal, Optional, Union, List
import re
import boto3
import os
import uuid
import logging

from serpapi import GoogleSearch
import time
from urllib.parse import urlparse
import requests
from bs4 import BeautifulSoup

from dotenv import load_dotenv

load_dotenv()


from langchain_core.documents import Document
from langchain.chat_models import init_chat_model
from langchain_core.language_models import BaseChatModel

logger = logging.getLogger(__name__)

def _format_doc(doc: Document) -> str:
    """Format a single document as XML.

    Args:
        doc (Document): The document to format.

    Returns:
        str: The formatted document as an XML string.
    """
    metadata = doc.metadata or {}
    meta = "".join(f" {k}={v!r}" for k, v in metadata.items())
    if meta:
        meta = f" {meta}"

    return f"<document{meta}>\n{doc.page_content}\n</document>"

def remove_code_file_placeholders(docs: List[Document]) -> List[Document]:
    """Remove code file placeholder markers from document content.

    Args:
        docs (List[Document]): List of document objects that have a page_content attribute
            containing text that may include code file placeholders.

    Returns:
        List[Document]: The same list of documents with code file placeholders removed
            from their page_content.
    """
    for doc in docs:
        doc.page_content = re.sub(r'\[CODE FILE: [^\]]+\]', '', doc.page_content)
    return docs

def replace_s3_locations_with_content(docs: List[Document]) -> List[Document]:
    """Replace S3 location strings in document content with actual file contents.

    Args:
        docs (List[Document]): List of document objects that have a page_content attribute
            containing text that may include S3 locations.

    Returns:
        List[Document]: The same list of documents with S3 locations replaced with actual content.
    """
    s3_client = boto3.client('s3', 
                            aws_access_key_id=os.environ.get("AWS_ACCESS_KEY_ID", "not_provided"),
                            aws_secret_access_key=os.environ.get("AWS_SECRET_ACCESS_KEY", "not_provided"))

    for doc in docs:
        s3_locations = re.findall(r's3://[^\s\n]+', doc.page_content)
        for s3_location in s3_locations:
            try:
                bucket, key = s3_location.replace('s3://', '').split('/', 1)
                response = s3_client.get_object(Bucket=bucket, Key=key)
                file_content = response['Body'].read().decode('utf-8')
                doc.page_content = doc.page_content.replace(s3_location, file_content)
            
            except Exception as e:
                logger.error(f"Error processing {s3_location}: {e}")
    
    return docs

def load_chat_model(fully_specified_name: str, max_tokens: int = 4096) -> BaseChatModel:
    """Load a chat model from a fully specified name.

    Args:
        fully_specified_name (str): String in the format 'provider/model'.
    """
    if "/" in fully_specified_name:
        provider, model = fully_specified_name.split("/", maxsplit=1)
    else:
        provider = ""
        model = fully_specified_name

    model_kwargs = {
        "temperature": 0,
        "max_tokens": max_tokens
    }
    return init_chat_model(model, model_provider=provider, **model_kwargs)

def reduce_docs(
    existing: Optional[list[Document]],
    new: Union[
        list[Document],
        list[dict[str, Any]],
        list[str],
        str,
        Literal["delete"],
    ],
) -> list[Document]:
    """Reduce and process documents based on the input type.

    This function handles various input types and converts them into a sequence of Document objects.
    It also combines existing documents with the new one based on the document ID.

    Args:
        existing (Optional[Sequence[Document]]): The existing docs in the state, if any.
        new (Union[Sequence[Document], Sequence[dict[str, Any]], Sequence[str], str, Literal["delete"]]):
            The new input to process. Can be a sequence of Documents, dictionaries, strings, or a single string.
    """
    if new == "delete":
        return []

    existing_list = list(existing) if existing else []
    if isinstance(new, str):
        return existing_list + [
            Document(page_content=new, metadata={"uuid": str(uuid.uuid4())})
        ]

    new_list = []
    if isinstance(new, list):
        existing_ids = set(doc.metadata.get("uuid") for doc in existing_list)
        for item in new:
            if isinstance(item, str):
                item_id = str(uuid.uuid4())
                new_list.append(Document(page_content=item, metadata={"uuid": item_id}))
                existing_ids.add(item_id)

            elif isinstance(item, dict):
                metadata = item.get("metadata", {})
                item_id = metadata.get("uuid", str(uuid.uuid4()))

                if item_id not in existing_ids:
                    new_list.append(
                        Document(**item, metadata={**metadata, "uuid": item_id})
                    )
                    existing_ids.add(item_id)

            elif isinstance(item, Document):
                item_id = item.metadata.get("uuid")
                if item_id is None:
                    item_id = str(uuid.uuid4())
                    new_item = item.copy(deep=True)
                    new_item.metadata["uuid"] = item_id
                else:
                    new_item = item

                if item_id not in existing_ids:
                    new_list.append(new_item)
                    existing_ids.add(item_id)

    return existing_list + new_list

def format_docs_code(docs: Optional[list[Document]], code: Optional[list[str]]) -> str:
    """Format a list of documents and code snippets as XML.

    This function takes a list of Document objects and a list of code snippets,
    and formats them into a single XML string.

    Args:
        docs (Optional[list[Document]]): A list of Document objects to format, or None.
        code (Optional[list[str]]): A list of code snippets to format, or None.

    Returns:
        str: A string containing the formatted documents and code in XML format.

    Examples:
        >>> docs = [Document(page_content="Hello"), Document(page_content="World")]
        >>> code = ["print('Hello')", "print('World')"]
        >>> print(format_docs(docs, code))
        <documents>
        <document>
        Hello
        </document>
        <document>
        World
        </document>
        </documents>
        <code>
        print('Hello')
        print('World')
        </code>

        >>> print(format_docs(None, None))
        <documents></documents>
        <code></code>
    """
    doc_content = "\n".join(_format_doc(doc) for doc in docs) if docs else ""

    if code:
        # Extract the first element from each tuple and join them with newlines
        code_snippets = [tup[0] for tup in code if tup and tup[0]]  # Skip empty tuples or empty strings
        code_content = "\n\n".join(code_snippets)  # Add double newline between code blocks for readability
    else:
        code_content = ""

    return f"""<documents>
{doc_content}
</documents>
<code>
{code_content}
</code>"""

def format_docs(docs: Optional[list[Document]]) -> str:
    """Format a list of documents and code snippets as XML.

    This function takes a list of Document objects and a list of code snippets,
    and formats them into a single XML string.

    Args:
        docs (Optional[list[Document]]): A list of Document objects to format, or None.
        code (Optional[list[str]]): A list of code snippets to format, or None.

    Returns:
        str: A string containing the formatted documents and code in XML format.

    Examples:
        >>> docs = [Document(page_content="Hello"), Document(page_content="World")]
        >>> code = ["print('Hello')", "print('World')"]
        >>> print(format_docs(docs, code))
        <documents>
        <document>
        Hello
        </document>
        <document>
        World
        </document>
        </documents>
        <code>
        print('Hello')
        print('World')
        </code>

        >>> print(format_docs(None, None))
        <documents></documents>
        <code></code>
    """
    doc_content = "\n".join(_format_doc(doc) for doc in docs) if docs else ""

    return f"""<documents>
{doc_content}
</documents>
"""

def reduce_codes(
    existing: Optional[list[tuple[str, ...]]],
    new: Union[
        list[tuple[str, ...]],
        tuple[str, ...],
        Literal["delete"]],
) -> list[tuple[str, ...]]:
    """Process code inputs and maintain the code list."""
    
    if new == "delete":
        return []
        
    existing_list = list(existing) if existing else []
    
    # Convert single tuple to list of tuples
    if isinstance(new, tuple):
        new = [new]
        
    if isinstance(new, list):
        # Add new codes only if they don't exist in the current list
        for code_tuple in new:
            # For debug printing, safely handle the tuple
            if code_tuple not in existing_list:
                existing_list.append(code_tuple)
    
    return existing_list



def web_search(query: str):
    """Finds general knowledge information using Google search."""
    SERPAPI_KEY=os.getenv('SERPAPI_KEY')

    SERPAPI_PARAMS = { "engine": "google",
    "api_key": SERPAPI_KEY,}
    search = GoogleSearch({
        **SERPAPI_PARAMS,
        "q": query,
        "num": 5
    })
    results = search.get_dict().get("organic_results", [])  # Ensure we extract "organic_results"
    return results


def scrape_url(url: str) -> str:
    try:
        response = requests.get(url)
        response.raise_for_status() 
        soup = BeautifulSoup(response.text, 'html.parser')
        return soup.get_text(separator='\n', strip=True)
    except Exception as e:
        print(f"Error scraping {url}: {e}")
        return ""
    
def extract_domain(url: str) -> str:
    """Extracts the second-level domain name from a given URL."""
    try:
        parsed_url = urlparse(url)
        domain_parts = parsed_url.netloc.split('.')  # Split the domain into parts
        if len(domain_parts) > 1:
            return domain_parts[-2]  # Returns 'justanswer' from 'www.justanswer.com'
        else:
            return parsed_url.netloc  # If no subdomains exist, just return the netloc
    except Exception as e:
        print(f"Error extracting domain: {e}")
        return ""