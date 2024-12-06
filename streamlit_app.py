import streamlit as st
from auth.register import register_user
from auth.Login import login
from auth.Logout import logout
from features.how_to_guide_page import how_to_guide_interface
from features.error_handling_page import error_handling_interface

# Landing page function
def landing_page():
    st.title("🐍 Python Library Coding Agent")
    
    # Add a descriptive section about the app

    # Main description
    st.markdown("""
    Welcome to Python Library Coding Agent - where natural language meets code intelligence. 
    We simplify your development workflow by providing smart, conversational access to Python library knowledge and implementation.
    ### ⚡ Key Features
    Unlock powerful capabilities that streamline your development process
    with intelligent repository management and interactive learning experiences.
    
    - **Smart Repository Integration:**
        Upload and access any Python library instantly
    - **Interactive Learning:**
        Custom installation guides and tutorials
    - **Code Generation & API Mastery:**
        Ready-to-use code snippets
    - **Error Resolution:**
        Expert solutions and references
    """)

    # Authentication buttons in two columns at the bottom
    st.markdown("---")

    # Create columns for navigation
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("➡️ **Login**", use_container_width=True):
            st.session_state.current_page = 'login'
            st.rerun()
    
    with col2:
        if st.button("®️ **Register**", use_container_width=True):
            st.session_state.current_page = 'register'
            st.rerun()

# Initialize session state
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False

# Initialize current page state
if 'current_page' not in st.session_state:
    st.session_state.current_page = 'landing'

# Set page configuration
st.set_page_config(
    page_title='Open Source Code Agent',
    page_icon='🐍',
    layout='wide'
)

# Navigation based on current page and login state
if st.session_state.current_page == 'landing':
    landing_page()
elif st.session_state.current_page == 'login':
    login()
elif st.session_state.current_page == 'register':
    register_user()
elif st.session_state.logged_in and st.session_state.current_page == 'how_to_guide':
    how_to_guide_interface()
elif st.session_state.logged_in and st.session_state.current_page == 'error_handling':
    error_handling_interface()
elif st.session_state.current_page == 'logout':  # Handle logout page
    logout()
    if 'logged_in' not in st.session_state:  # After logout completes
        st.session_state.current_page = 'landing'
        st.rerun()

# Show navigation sidebar for logged-in users
if st.session_state.logged_in:
    with st.sidebar:
        st.title(f"Welcome, {st.session_state.get('user_name', 'User')}")
        
        if st.button("📖 How-to Guide"):
            st.session_state.current_page = 'how_to_guide'
            st.rerun()

        if st.button("🚨 Error Handling"):
            st.session_state.current_page = 'error_handling'
            st.rerun()
            
        if st.button("🚪 Logout"):
            st.session_state.current_page = 'logout'
            st.rerun()