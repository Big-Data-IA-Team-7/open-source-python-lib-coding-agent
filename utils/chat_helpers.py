import streamlit as st
import logging
from typing import Optional
from utils.chunk_processors import process_app_build, process_content_with_download, process_error, process_research_documents, process_research_plan, process_response

logger = logging.getLogger(__name__)

def process_stream(line: str) -> Optional[str]:
    """Process the streaming response with structured formatting."""
    if not (line and line.startswith("data: ")):
        return None
        
    current_chunk = line[6:].strip()
    if not current_chunk:
        return None

    try:
        # Map of chunk types to their processing functions
        chunk_processors = {
            "'conduct_research'": (process_research_documents, None),
            "'create_research_plan'": (process_research_plan, None),
            "'create_app_research_plan'": (process_research_plan, None),
            "'build_app'": (process_app_build, None),
            "'respond'": (process_response, lambda x: x),
            "'handle_error'": (process_error, lambda x: x),
            "'generate_requirements_txt'": (
                lambda chunk: process_content_with_download(
                    chunk,
                    "requirements.txt",
                    "📦 View requirements.txt",
                    'code'
                ),
                None
            ),
            "'generate_readme_md'": (
                lambda chunk: process_content_with_download(
                    chunk,
                    "README.md",
                    "📖 View README.md",
                    'markdown'
                ),
                None
            )
        }

        # Update progress based on chunk type
        for chunk_type in chunk_processors.keys():
            if chunk_type in current_chunk:
                # Remove quotes from chunk type
                clean_chunk_type = chunk_type.replace("'", "")
                # Call the progress update function
                st.session_state.get('update_progress', lambda x: None)(clean_chunk_type)
                break

        # Process the chunk based on its type
        for chunk_type, (processor, return_handler) in chunk_processors.items():
            if chunk_type in current_chunk:
                result = processor(current_chunk)
                return return_handler(result) if return_handler else None

        return current_chunk

    except Exception as e:
        logger.error(f"Exception occurred in main processing: {e}")
        st.error(f"Exception occurred in main processing: {e}")
        return None