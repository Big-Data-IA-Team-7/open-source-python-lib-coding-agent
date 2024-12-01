import streamlit as st
import traceback
import asyncio
from utils.api_helpers import generatecode_api
from utils.chat_helpers import process_stream

def safe_chat_interface():
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

        st.title("Chat Interface")

        # Display chat history
        try:
            for message in st.session_state['history']:
                with st.chat_message(message["role"]):
                    st.markdown(message["content"])
        except Exception as history_error:
            st.warning("Error displaying chat history. The history may be reset.")
            st.session_state['history'] = []

        # Chat input
        user_input = st.chat_input("Enter your query:")

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
                        response = asyncio.run(generatecode_api(
                            user_input, 
                            st.session_state['history'],
                            st.session_state['token']
                        ))
                        
                        if response.status_code == 401:
                            st.error("Authentication failed. Please log in again.")
                            return
                        elif response.status_code != 200:
                            raise Exception(f"API returned status code {response.status_code}")
                        
                        # Process the streaming response in an async function
                        full_response = asyncio.run(process_stream(response, message_placeholder))
                        
                        # Final update without cursor
                        if full_response:
                            st.session_state['last_response'] = full_response
                            st.session_state['history'].append({
                                "role": "assistant", 
                                "content": full_response
                            })
                            st.session_state['feedback_given'] = False
                        
                    except Exception as stream_error:
                        if "Stream cancelled by user" in str(stream_error):
                            message_placeholder.warning("Response generation was cancelled.")
                        else:
                            message_placeholder.error(f"Error processing response: {str(stream_error)}")
                        return

            except Exception as response_error:
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
                    st.success("Thank you for your feedback!")

            with col2:
                if st.button("No", key="feedback_negative", disabled=st.session_state.get('feedback_given', False)):
                    st.session_state['feedback_given'] = True
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
        st.error("A critical error occurred. Please refresh the page.")
        st.error(f"Error details: {str(e)}")
        st.text_area("Error Traceback:", value=traceback.format_exc(), height=200)