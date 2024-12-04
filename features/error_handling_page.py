import streamlit as st
import traceback
from utils.api_helpers import stream_code_generation

def error_handling_interface():
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

        st.title("Error Handler")
        
        st.markdown("""
        Get help debugging your code by providing context, code, and the error message.
        Our AI will analyze the issue and suggest solutions.
        """)

        # Input sections
        with st.expander("Enter Error Details", expanded=True):
            # Context input
            context = st.text_area(
                "Context",
                placeholder="Describe what you're trying to do and any relevant background information...",
                height=100
            )

            # Code input
            code = st.text_area(
                "Code",
                placeholder="Paste your code here...",
                height=200
            )

            # Error message input
            error_message = st.text_area(
                "Error Message",
                placeholder="Paste the error message/stack trace here...",
                height=150
            )

            # Submit button
            submit = st.button("Analyze Error")

        # Display chat history
        try:
            for message in st.session_state['history']:
                with st.chat_message(message["role"]):
                    st.markdown(message["content"])
        except Exception as history_error:
            st.warning("Error displaying chat history. The history may be reset.")
            st.session_state['history'] = []

        # Handle form submission
        if submit and (context.strip() or code.strip() or error_message.strip()):
            try:
                # Prepare the combined query
                user_query = f"""
                Context:
                {context}

                Code:
                ```
                {code}
                ```

                Error Message:
                ```
                {error_message}
                ```
                """

                # Display user message
                with st.chat_message("user"):
                    st.markdown(user_query)
                st.session_state['history'].append({"role": "user", "content": user_query})

                # Call API and display streaming response
                with st.chat_message("assistant"):
                    message_placeholder = st.empty()
                    try:
                        # Get the response
                        full_response = stream_code_generation(user_query, st.session_state['history'])
                        
                        if full_response:
                            st.session_state['last_response'] = full_response
                            st.session_state['history'].append({
                                "role": "assistant", 
                                "content": full_response
                            })
                            st.session_state['feedback_given'] = False
                        else:
                            error_message = "Sorry, I couldn't analyze the error. Please try again."
                            message_placeholder.markdown(error_message)
                            st.session_state['last_response'] = error_message
                            st.session_state['history'].append({
                                "role": "assistant", 
                                "content": error_message
                            })
                        
                    except Exception as stream_error:
                        if "Stream cancelled by user" in str(stream_error):
                            message_placeholder.warning("Analysis was cancelled.")
                        else:
                            message_placeholder.error(f"Error processing response: {str(stream_error)}")
                        return

            except Exception as response_error:
                st.error("An error occurred while processing your request.")
                st.session_state['last_error'] = {
                    'type': type(response_error).__name__,
                    'message': str(response_error),
                    'traceback': traceback.format_exc()
                }

        # Response Feedback Section
        if st.session_state.get('last_response'):
            st.markdown("---")
            st.markdown("**Was this solution helpful?**")
            
            col1, col2 = st.columns(2)
            
            with col1:
                if st.button("Yes", key="feedback_positive", disabled=st.session_state.get('feedback_given', False)):
                    st.session_state['feedback_given'] = True
                    st.success("Thank you for your feedback!")

            with col2:
                if st.button("No", key="feedback_negative", disabled=st.session_state.get('feedback_given', False)):
                    st.session_state['feedback_given'] = True
                    st.error("We're sorry the solution didn't help. Our team will work on improving.")

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