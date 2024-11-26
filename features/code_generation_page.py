import streamlit as st
import traceback
import sys

def safe_chat_interface():
    try:
        # Error handling for session state initialization
        if 'history' not in st.session_state:
            st.session_state['history'] = []
        if 'last_response' not in st.session_state:
            st.session_state['last_response'] = None
        if 'feedback_given' not in st.session_state:
            st.session_state['feedback_given'] = False
        
        # Add error tracking
        if 'last_error' not in st.session_state:
            st.session_state['last_error'] = None

        st.title("Chat Interface")

        # Chat input
        user_input = st.chat_input("Enter your query:")

        # Display chat history
        try:
            for message in st.session_state['history']:
                with st.chat_message(message["role"]):
                    st.markdown(message["content"])
        except Exception as history_error:
            st.warning("Error displaying chat history. The history may be reset.")
            st.session_state['history'] = []

        # Handle user input
        if user_input:
            try:
                # Display user message
                with st.chat_message("user"):
                    st.markdown(user_input)
                st.session_state['history'].append({"role": "user", "content": user_input})

                # Simulate bot response (replace with actual AI response logic later)
                with st.chat_message("assistant"):
                    response = f"This is a simulated response to: {user_input}"
                    st.markdown(response)
                
                # Store the last response
                st.session_state['last_response'] = response
                st.session_state['history'].append({"role": "assistant", "content": response})
                st.session_state['feedback_given'] = False

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
        # Catch-all error handling
        st.error("A critical error occurred. Please refresh the page.")
        st.error(f"Error details: {str(e)}")
        
        # Log the full traceback
        st.text_area("Error Traceback:", value=traceback.format_exc(), height=200)

def main():
    try:
        safe_chat_interface()
    except Exception as e:
        st.error("An unexpected error occurred. Please refresh the page.")
        st.error(f"Error: {str(e)}")
        # Optional: log the full traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()