import streamlit as st
from auth.register import register_user
from auth.login import login
from auth.logout import logout

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
        # Using emoji icons
        if st.button("➡️ **Login**", use_container_width=True):
            st.session_state.current_page = 'login'
            st.rerun()
    
    with col2:
        # Using emoji icons
        if st.button("®️ **Register**", use_container_width=True):
            st.session_state.current_page = 'register'
            st.rerun()

# Initialize session state
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False

# Initialize current page state
if 'current_page' not in st.session_state:
    st.session_state.current_page = 'landing'

# Define pages
landing_page_nav = st.Page(landing_page, title='Landing', icon=':material/home:')
login_page = st.Page(login, title='Login', icon=':material/login:')
register_page = st.Page(register_user, title='Register', icon=':material/person_add:')
logout_page = st.Page(logout, title='Logout', icon=':material/logout:')

# Navigation logic
if st.session_state.current_page == 'landing':
    pg = st.navigation([landing_page_nav])
elif st.session_state.logged_in:
    pg = st.navigation({
        "Account": [logout_page]
    })
elif st.session_state.current_page == 'register':
    pg = st.navigation([register_page])
else:
    pg = st.navigation([login_page])

# Set page configuration
st.set_page_config(page_title='Open Source Code Agent', page_icon=':material/lock:')

# Run the selected page
pg.run()

