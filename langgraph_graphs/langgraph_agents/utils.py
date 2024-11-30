from typing import Any, Literal, Optional, Union, List
import re
import boto3
import os

from langchain_core.documents import Document
from langchain.chat_models import init_chat_model
from langchain_core.language_models import BaseChatModel

import uuid

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