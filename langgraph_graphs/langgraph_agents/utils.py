from typing import Any, Literal, Optional, Union, List
import re
import boto3
import os
import uuid

from langchain_core.documents import Document
from langchain.chat_models import init_chat_model
from langchain_core.language_models import BaseChatModel

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

def _format_code(code: str) -> str:
    """Format a single code snippet as XML."""
    return f"<code>\n{code}\n</code>"

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
                print(f"Error processing {s3_location}: {e}")
    
    return docs

def load_chat_model(fully_specified_name: str) -> BaseChatModel:
    """Load a chat model from a fully specified name.

    Args:
        fully_specified_name (str): String in the format 'provider/model'.
    """
    if "/" in fully_specified_name:
        provider, model = fully_specified_name.split("/", maxsplit=1)
    else:
        provider = ""
        model = fully_specified_name

    model_kwargs = {"temperature": 0}
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
    code_content = "\n".join(_format_code(c) for c in code) if code else ""

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

def append_code(existing: list[str], new_codes: list[str]) -> list[str]:
    """Reducer function to append new codes to the list if they don't already exist."""
    if existing is None:
        return new_codes
    
    # Create a set of existing codes for faster lookup
    existing_set = set(existing)
    
    # Only append codes that don't already exist
    unique_new_codes = [code for code in new_codes if code not in existing_set]
    
    return existing + unique_new_codes