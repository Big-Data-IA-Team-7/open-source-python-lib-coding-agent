import streamlit as st
import traceback
from utils.api_helpers import stream_application_build
import logging

def code_generation_interface():
    logger = logging.getLogger(__name__)
    try:
        # Error handling for session state initialization
        if 'history_cg' not in st.session_state:
            st.session_state['history_cg'] = []
        if 'code_response' not in st.session_state:
            st.session_state['code_response'] = None
        if 'last_error_cg' not in st.session_state:
            st.session_state['last_error_cg'] = None
        if 'token' not in st.session_state:
            st.error("Please log in first")
            return

        st.title("App Builder")
        
        st.markdown("""
        Build a complete LangGraph application using Streamlit for your usecase. Try an example or enter your own query below:
        """)

        col1, col2 = st.columns(2)
        example1 = "Create a LangGraph application for a Code Generation Assistant that can understand programming requirements, generate code with proper documentation, handle edge cases, and provide explanations for the implementation."
        example2 = "Build a LangGraph application for a PDF-based RAG agent that can process PDF documents, extract relevant information, create embeddings, handle semantic search, and provide contextual responses with source citations."

        with col1:
            st.markdown(":computer: **Code Generation Assistant**", 
                    help=example1)
                
        with col2:
            st.markdown(":page_facing_up: **PDF-based RAG Agent**",
                    help=example2)

        # Display chat history
        try:
            for message in st.session_state['history_cg']:
                with st.chat_message(message["role"]):
                    st.markdown(message["content"])
        except Exception as history_error:
            logger.warning("Error displaying chat history. The history may be reset.")
            st.warning("Error displaying chat history. The history may be reset.")
            st.session_state['history_cg'] = []

        # Chat input
        user_input = st.chat_input("Enter your query:")

        if 'example_query' in st.session_state:
            del st.session_state['example_query']

        # Handle user input
        if user_input:
            try:
                # Display user message
                with st.chat_message("user"):
                    st.markdown(user_input)
                st.session_state['history_cg'].append({"role": "user", "content": user_input})

                # Call API and display streaming response
                with st.chat_message("assistant"):
                    message_placeholder = st.empty()
                    try:
                        # Get the response
                        # Use asyncio.run for the top-level async call
                        full_response = stream_application_build(user_input, st.session_state['history_cg'])
                        
                        # # Update session state if response is received
                        if full_response:
                            st.session_state['code_response'] = full_response
                            st.session_state['history_cg'].append({
                                "role": "assistant", 
                                "content": full_response
                            })
                        else:
                            # Handle empty response
                            error_message = "Sorry, I couldn't generate a response. Please try again."
                            message_placeholder.markdown(error_message)
                            st.session_state['code_response'] = error_message
                            st.session_state['history_cg'].append({
                                "role": "assistant", 
                                "content": error_message
                            })
                        
                    except Exception as stream_error:
                        if "Stream cancelled by user" in str(stream_error):
                            logger.warning("Response generation was cancelled.")
                            message_placeholder.warning("Response generation was cancelled.")
                        else:
                            logger.error(f"Error processing response: {str(stream_error)}")
                            message_placeholder.error(f"Error processing response: {str(stream_error)}")
                        return

            except Exception as response_error:
                logger.error("An error occurred while processing your message.")
                st.error("An error occurred while processing your message.")
                st.session_state['last_error_cg'] = {
                    'type': type(response_error).__name__,
                    'message': str(response_error),
                    'traceback': traceback.format_exc()
                }

        # Clear chat button
        if st.button("Clear Chat"):
            st.session_state['history_cg'] = []
            st.session_state['code_response'] = None
            st.rerun()

        # Error Logging and Display
        if st.session_state.get('last_error_cg'):
            with st.expander("Debug Information"):
                error = st.session_state['last_error_cg']
                st.write("An error occurred:")
                st.write(f"Error Type: {error['type']}")
                st.write(f"Error Message: {error['message']}")
                st.text_area("Detailed Traceback:", value=error['traceback'], height=200)

    except Exception as e:
        logger.error(f"Critical Error. Error details: {str(e)}")
        st.error("A critical error occurred. Please refresh the page.")
        st.error(f"Error details: {str(e)}")
        st.text_area("Error Traceback:", value=traceback.format_exc(), height=200)