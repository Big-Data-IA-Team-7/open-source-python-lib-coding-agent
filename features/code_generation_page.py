import streamlit as st

def chat_interface():
    st.title("Chat Interface")

    # Initialize session state
    if 'history' not in st.session_state:
        st.session_state['history'] = []
    if 'last_response' not in st.session_state:
        st.session_state['last_response'] = None
    if 'feedback_given' not in st.session_state:
        st.session_state['feedback_given'] = False

    # Chat input
    user_input = st.chat_input("Enter your query:")

    # Display chat history
    for message in st.session_state['history']:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # Handle user input
    if user_input:
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

def main():
    chat_interface()

if __name__ == "__main__":
    main()