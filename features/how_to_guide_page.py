import streamlit as st
import traceback
from utils.api_helpers import stream_code_generation
import logging

def how_to_guide_interface():
    logger = logging.getLogger(__name__)
    try:
        # Error handling for session state initialization
        if 'history' not in st.session_state:
            st.session_state['history'] = []
        if 'last_response' not in st.session_state:
            st.session_state['last_response'] = None
        if 'feedback_given' not in st.session_state:
            st.session_state['feedback_given'] = False
        if 'last_error' not in st.session_state:
            st.session_state['last_error'] = None
        if 'token' not in st.session_state:
            st.error("Please log in first")
            return

        st.title("📖 How-to Guide")
        
        st.markdown("""
        Get step-by-step guides to build LangGraph applications for your use case. 
        Try an example or enter your own query below:
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
            for message in st.session_state['history']:
                with st.chat_message(message["role"]):
                    st.markdown(message["content"])
        except Exception as history_error:
            logger.warning("Error displaying chat history. The history may be reset.")
            st.warning("Error displaying chat history. The history may be reset.")
            st.session_state['history'] = []

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
                st.session_state['history'].append({"role": "user", "content": user_input})

                # Call API and display streaming response
                with st.chat_message("assistant"):
                    message_placeholder = st.empty()
                    try:
                        # Get the response
                        # Use asyncio.run for the top-level async call
                        full_response = stream_code_generation(user_input, st.session_state['history'])
                        
                        # # Update session state if response is received
                        if full_response:
                            st.session_state['last_response'] = full_response
                            st.session_state['history'].append({
                                "role": "assistant", 
                                "content": full_response
                            })
                            st.session_state['feedback_given'] = False
                        else:
                            # Handle empty response
                            error_message = "Sorry, I couldn't generate a response. Please try again."
                            message_placeholder.markdown(error_message)
                            st.session_state['last_response'] = error_message
                            st.session_state['history'].append({
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
                st.session_state['last_error'] = {
                    'type': type(response_error).__name__,
                    'message': str(response_error),
                    'traceback': traceback.format_exc()
                }

        # Response Feedback Section
        if st.session_state.get('last_response'):
            st.markdown("---")
            st.markdown("**Did this response solve your problem?**")
            
            col1, col2 = st.columns(2)
            
            with col1:
                if st.button("Yes", key="feedback_positive", disabled=st.session_state.get('feedback_given', False)):
                    st.session_state['feedback_given'] = True
                    logger.info("Thank you for your feedback!")
                    st.success("Thank you for your feedback!")

            with col2:
                if st.button("No", key="feedback_negative", disabled=st.session_state.get('feedback_given', False)):
                    st.session_state['feedback_given'] = True
                    logger.info("We're sorry the response didn't help. Our team will work on improving.")
                    st.error("We're sorry the response didn't help. Our team will work on improving.")

        # Clear chat button
        if st.button("Clear Chat"):
            st.session_state['history'] = []
            st.session_state['last_response'] = None
            st.session_state['feedback_given'] = False
            st.rerun()

        # Error Logging and Display
        if st.session_state.get('last_error'):
            with st.expander("Debug Information"):
                error = st.session_state['last_error']
                st.write("An error occurred:")
                st.write(f"Error Type: {error['type']}")
                st.write(f"Error Message: {error['message']}")
                st.text_area("Detailed Traceback:", value=error['traceback'], height=200)

    except Exception as e:
        logger.error(f"Critical Error. Error details: {str(e)}")
        st.error("A critical error occurred. Please refresh the page.")
        st.error(f"Error details: {str(e)}")
        st.text_area("Error Traceback:", value=traceback.format_exc(), height=200)