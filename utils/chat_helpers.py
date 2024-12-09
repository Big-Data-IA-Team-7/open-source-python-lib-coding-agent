import streamlit as st
import logging
import re

logger = logging.getLogger(__name__)

def extract_metadata_from_document_string(doc_str: str) -> dict:
    """Extract metadata from a Document string representation."""
    # Extract metadata section using regex
    metadata_match = re.search(r"metadata=({[^}]+})", doc_str)
    if not metadata_match:
        return {}
    
    try:
        # Clean up the metadata string and evaluate it
        metadata_str = metadata_match.group(1)
        metadata_str = metadata_str.replace("'", '"')  # standardize quotes
        import json
        metadata = json.loads(metadata_str)
        return metadata
    except Exception as e:
        logger.error(f"Error parsing metadata: {e}")
        return {}

def preprocess_content(content: str) -> str:
    # Replace single `\n` with double newlines for proper markdown rendering
    content = content.replace("\\n", "\n")
    
    # Ensure triple backticks are properly spaced for code blocks
    content = content.replace("```", "\n```")
    
    return content

def process_stream(line: str):
    """Process the streaming response with structured formatting
    
    Args:
        line: Decoded string from the stream
    Returns:
        str: Processed response content
    """
    current_chunk = ""
    if line and line.startswith("data: "):
        logger.debug(f"Data Chunk: {line}")
        content = line[6:].strip()
        if content:
            current_chunk += content

            try:
                # First check data type without using eval
                if "'conduct_research'" in current_chunk:
                    logger.debug(f"Document Data: {current_chunk}")
                    try:
                        # Find all Document instances using regex
                        document_matches = re.finditer(r"Document\([^)]+\)", current_chunk)
                        
                        formatted_output = st.container()
                        with formatted_output:
                            # Extract and display current step if present
                            step_match = re.search(r"'current_step': '([^']+)'", current_chunk)
                            if step_match:
                                current_step = step_match.group(1)
                                st.markdown("### Step")
                                st.markdown(current_step)
                            
                            # Display document metadata
                            st.markdown("#### Relevant Documents")
                            for i, match in enumerate(list(document_matches)[:3], 1):
                                doc_str = match.group(0)
                                metadata = extract_metadata_from_document_string(doc_str)
                                
                                st.markdown(
                                    f"""
                                    <div style="
                                        padding: 15px; 
                                        border-radius: 5px; 
                                        background-color: #f0f2f6;
                                        margin: 10px 0;
                                    ">
                                        <b>{i}. {metadata.get('title', 'No Title')}</b><br>
                                        <i>{metadata.get('description', 'No description available')}</i><br>
                                        <a href="{metadata.get('source', '#')}" target="_blank">Source Link</a>
                                    </div>
                                    """, 
                                    unsafe_allow_html=True
                                )
                        
                        return None
                        
                    except Exception as e:
                        logger.error(f"Error processing research data: {e}")
                        st.error(f"Error processing research data: {e}")
                    
                    return
                
                elif "'create_research_plan'" in current_chunk:
                    # Only evaluate for research plan data
                    try:
                        data = eval(current_chunk)
                        plan = data.get('create_research_plan', {})
                        steps = plan.get('steps', [])

                        formatted_output = st.container()
                        with formatted_output:
                            st.markdown("### Research Steps")
                            
                            for i, step in enumerate(steps, 1):
                                st.markdown(
                                    f"""
                                    <div style="
                                        padding: 10px; 
                                        border-radius: 5px; 
                                        background-color: #f0f2f6;
                                        margin: 5px 0;
                                    ">
                                        <b>Step {i}</b><br>{step}
                                    </div>
                                    """, 
                                    unsafe_allow_html=True
                                )
                        
                        return None
                    
                    except Exception as e:
                        logger.error(f"Error processing research plan: {e}")
                        st.error(f"Error processing research plan: {e}")
                    
                elif "'respond'" in current_chunk:
                    # Handle AIMessage format using string parsing for both quote types
                    logger.debug(f"Respond Chunk: {current_chunk}")
                    st.markdown("### Final Answer")
                    start_markers = ["content='", 'content="']
                    end_markers = ["', additional_kwargs", '", additional_kwargs']
                    
                    message_content = None
                    
                    # Try each combination of start and end markers
                    for start_marker, end_marker in zip(start_markers, end_markers):
                        start_idx = current_chunk.find(start_marker)
                        if start_idx != -1:
                            start_idx += len(start_marker)
                            end_idx = current_chunk.find(end_marker, start_idx)
                            if end_idx != -1:
                                message_content = current_chunk[start_idx:end_idx]
                                break
                    
                    if message_content is not None:
                        processed_content = preprocess_content(message_content)
                        st.markdown(processed_content)
                        return processed_content
                elif "'handle_error'" in current_chunk:
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
                                    
            except Exception as e:
                logger.error(f"Exception occurred in main processing: {e}")
                st.error(f"Exception occurred in main processing: {e}")
                return None
            
            return current_chunk
    
    return None