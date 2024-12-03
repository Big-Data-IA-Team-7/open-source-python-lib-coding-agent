import streamlit as st

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
        content = line[6:].strip()
        if content:
            current_chunk += content

            try:
                # First check data type without using eval
                if "'conduct_research'" in current_chunk:
                    print("Skipping conduct_research data")
                    current_chunk = ""
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
                        st.error(f"Error processing research plan: {e}")
                    
                elif "'respond'" in current_chunk:
                    # Handle AIMessage format using string parsing for both quote types
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
                
            except Exception as e:
                st.error(f"Exception occurred in main processing: {e}")
                return None
            
            return current_chunk
    
    return None