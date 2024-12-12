import streamlit as st
import logging
import re
from typing import Optional

logger = logging.getLogger(__name__)

def preprocess_content(content: str) -> str:
    """Preprocess content for proper markdown rendering."""
    content = content.replace("\\n", "\n")
    content = content.replace("```", "\n```")
    return content

def preprocess_requirements(content: str) -> str:
    """Preprocess requirements.txt content by removing code blocks and extra whitespace."""
    # Remove code block markers
    content = content.replace('```', '')
    
    # Replace escaped newlines with actual newlines
    content = content.replace('\\n', '\n')
    
    # Handle literal backslashes properly
    content = content.replace('\\', '')
    
    # Remove extra whitespace and trailing/leading newlines
    content = content.strip()
    
    return content

def extract_message_content(current_chunk: str) -> Optional[str]:
    """Extract content from message chunks using different quote patterns."""
    start_markers = ["content='", 'content="']
    end_markers = ["', additional_kwargs", '", additional_kwargs']
    
    for start_marker, end_marker in zip(start_markers, end_markers):
        start_idx = current_chunk.find(start_marker)
        if start_idx != -1:
            start_idx += len(start_marker)
            end_idx = current_chunk.find(end_marker, start_idx)
            if end_idx != -1:
                return current_chunk[start_idx:end_idx]
    return None

def display_document_card(index: int, title: str, description: str, source: str) -> None:
    """Display a document card with consistent styling."""
    st.markdown(
        f"""
        <div style="
            padding: 15px; 
            border-radius: 5px; 
            background-color: #f0f2f6;
            margin: 10px 0;
        ">
            <b>{index}. {title or 'No Title'}</b><br>
            <i>{description or 'No description available'}</i><br>
            <a href="{source or '#'}" target="_blank">Source Link</a>
        </div>
        """, 
        unsafe_allow_html=True
    )

def process_research_documents(current_chunk: str) -> None:
    """Process and display research document data."""
    logger.debug(f"Document Data: {current_chunk}")
    try:
        document_matches = re.finditer(
            r"Document\(id='[^']+',\s*metadata={'description':\s*'([^']+)',\s*'source':\s*'([^']+)',\s*'title':\s*'([^']+)'[^)]+\)", 
            current_chunk
        )

        formatted_output = st.container()
        with formatted_output:
            step_match = re.search(r"'current_step': '([^']+)'", current_chunk)
            if step_match:
                st.markdown("### Step")
                st.markdown(step_match.group(1))
            
            st.markdown("#### Relevant Documents")
            for i, match in enumerate(list(document_matches)[:3], 1):
                description, source, title = match.groups()
                
                logging.debug(f"Title: {title}")
                logging.debug(f"Description: {description}")
                logging.debug(f"Source: {source}")
                
                display_document_card(i, title, description, source)
    except Exception as e:
        logger.error(f"Error processing research data: {e}")
        st.error(f"Error processing research data: {e}")

def display_step_card(index: int, step: str) -> None:
    """Display a step card with consistent styling."""
    st.markdown(
        f"""
        <div style="
            padding: 10px; 
            border-radius: 5px; 
            background-color: #f0f2f6;
            margin: 5px 0;
        ">
            <b>Step {index}</b><br>{step}
        </div>
        """, 
        unsafe_allow_html=True
    )

def process_research_plan(current_chunk: str) -> None:
    """Process and display research plan data."""
    try:
        data = eval(current_chunk)
        plan = data.get('create_research_plan', {}) or data.get('create_app_research_plan', {})
        steps = plan.get('steps', []) or plan.get('app_steps', [])

        formatted_output = st.container()
        with formatted_output:
            st.markdown("### Application Steps")
            for i, step in enumerate(steps, 1):
                display_step_card(i, step)
    except Exception as e:
        logger.error(f"Error processing research plan: {e}")
        st.error(f"Error processing research plan: {e}")

def display_code_header(filename: str) -> None:
    """Display a code file header with consistent styling."""
    st.markdown(
        f"""
        <div style="
            padding: 10px;
            border-radius: 5px;
            background-color: #f0f2f6;
            margin: 10px 0;
        ">
            <b>{filename}</b>
        </div>
        """, 
        unsafe_allow_html=True
    )

def process_app_build(current_chunk: str) -> None:
    """Process and display application build data."""
    if not st.session_state.final_output:
        st.session_state.final_output = True
        return
    
    st.session_state.final_output = False
    try:
        data = eval(current_chunk)
        app_data = data.get('build_app', {})
        
        formatted_output = st.container()
        with formatted_output:
            st.markdown("### Application Code")
            
            for file_name in ['frontend.py', 'backend.py']:
                key = file_name.split('.')[0]
                display_code_header(file_name)
                st.code(app_data.get(key, ''), language='python')
            
            col1, col2 = st.columns(2)
            for col, file_name in zip([col1, col2], ['frontend.py', 'backend.py']):
                with col:
                    key = file_name.split('.')[0]
                    code = app_data.get(key, '')
                    st.download_button(
                        label=f"Download {file_name}",
                        data=code,
                        file_name=file_name,
                        mime="text/plain"
                    )
    except Exception as e:
        logger.error(f"Error processing build_app: {e}")
        st.error(f"Error processing build_app: {e}")

def process_content_with_download(
    current_chunk: str,
    file_name: str,
    expander_title: str,
    display_type: str = 'code'
) -> None:
    """Process content and provide download option with consistent formatting."""
    logger.debug(f"{file_name} Data: {current_chunk}")
    try:
        content = extract_message_content(current_chunk)
        if content is not None:
            # Special handling for requirements.txt
            if file_name == "requirements.txt":
                processed_content = preprocess_requirements(content)
            else:
                processed_content = preprocess_content(content)
                
            formatted_output = st.container()
            with formatted_output:
                with st.expander(expander_title):
                    if display_type == 'markdown':
                        st.markdown(processed_content)
                    else:
                        st.code(processed_content, language='text')
                    st.download_button(
                        label=f"Download {file_name}",
                        data=processed_content,
                        file_name=file_name,
                        mime="text/plain"
                    )
    except Exception as e:
        logger.error(f"Error processing {file_name}: {e}")
        st.error(f"Error processing {file_name}: {e}")

def process_response(current_chunk: str) -> Optional[str]:
    """Process response chunks."""
    logger.debug(f"Respond Chunk: {current_chunk}")
    st.markdown("### Final Answer")
    content = extract_message_content(current_chunk)
    if content is not None:
        processed_content = preprocess_content(content)
        st.markdown(processed_content)
        return processed_content
    return None

def process_error(current_chunk: str) -> Optional[str]:
    """Process error chunks."""
    try:
        data = eval(current_chunk)
        error_content = data.get('handle_error', {}).get('answer', '')
        if error_content:
            processed_content = preprocess_content(error_content)
            st.markdown(processed_content)
            return processed_content
    except Exception as e:
        logger.error(f"Error processing handle_error: {e}")
        st.error(f"Error processing handle_error: {e}")
    return None