import streamlit as st
import asyncio

def preprocess_content(content: str) -> str:
    # Replace single `\n` with double newlines for proper markdown rendering
    content = content.replace("\\n", "\n")
    
    # Ensure triple backticks are properly spaced for code blocks
    content = content.replace("```", "\n```")
    
    return content

async def process_stream(response, message_placeholder):
    """Async function to process the streaming response with structured formatting"""
    full_response = ""
    current_chunk = ""
    
    async for line in response.aiter_lines():
        if line and line.startswith("data: "):
            content = line[6:].strip()
            if content:
                current_chunk += content
                print("Current chunk length:", len(current_chunk))
                print("Current chunk preview:", current_chunk[:100] + "..." if len(current_chunk) > 100 else current_chunk)

                try:
                    # First check data type without using eval
                    if "'conduct_research'" in current_chunk:
                        print("Skipping conduct_research data")
                        current_chunk = ""
                        continue
                    
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
                        except Exception as e:
                            st.error(f"Error processing research plan: {e}")
                        
                    elif "'respond'" in current_chunk:
                        # Handle AIMessage format using string parsing
                        start_marker = "content='"
                        end_marker = "', additional_kwargs"
                        
                        start_idx = current_chunk.find(start_marker)
                        if start_idx != -1:
                            start_idx += len(start_marker)
                            end_idx = current_chunk.find(end_marker, start_idx)
                            if end_idx != -1:
                                message_content = current_chunk[start_idx:end_idx]
                                
                                processed_content = preprocess_content(message_content)
                                
                                st.markdown(processed_content)
                                full_response = message_content
                    
                except Exception as e:
                    st.error(f"Exception occurred in main processing: {e}")
                
                full_response = current_chunk
                
                # Reset chunk after processing
                current_chunk = ""
                
        await asyncio.sleep(0.01)
    
    return full_response