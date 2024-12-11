from dotenv import load_dotenv
import streamlit as st

from auth.register import register_user
from auth.Login import login
from auth.Logout import logout

from features.how_to_guide_page import how_to_guide_interface
from features.error_handling_page import error_handling_interface
from features.code_generation_page import code_generation_interface
from features.github_repo_page import github_repo_management
from features.github_credentials_page import github_credentials
from logging_module.logging_config import setup_logging

load_dotenv()
logger = setup_logging()

# Landing page function
def landing_page():
    st.title("🐍 Python Library Coding Agent")

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
elif st.session_state.logged_in and st.session_state.current_page == 'app_builder':
    code_generation_interface()
elif st.session_state.logged_in and st.session_state.current_page == 'github':
    github_repo_management()
elif st.session_state.logged_in and st.session_state.current_page == 'githubcredentials':
    github_credentials()
elif st.session_state.current_page == 'logout':  # Handle logout page
    logout()
    if 'logged_in' not in st.session_state:  # After logout completes
        st.session_state.current_page = 'landing'
        st.rerun()

# Show navigation sidebar for logged-in users
if st.session_state.logged_in:

    if st.session_state.current_page == 'code_generation':
            st.markdown("""
            # 📚 Welcome to Python Library Coding Agent 📚  
            ### Your Smart Companion for Python Library Mastery 🎓

            Harness the power of conversational intelligence to revolutionize your coding experience.  
            With our intuitive platform, you can streamline your development workflow and unlock new levels of productivity.

            ### 🛠 Key Features:  
            - **Instant Repository Management:** Quickly upload and access Python libraries.  
            - **Interactive Learning Tools:** Dive into tailored guides and tutorials.  
            - **Effortless Code Generation:** Create custom scripts and API implementations in seconds.  
            - **Error Resolution Made Easy:** Debug issues with expert recommendations and references.  

            ### 🎛️ Explore Platform Functionalities:
            Here’s what each button in the sidebar does:

            - **📖 How-to Guide:**  Access step-by-step tutorials and instructions to help you integrate and use various Python libraries effectively.  
            - **🚨 Error Handling:** Troubleshoot common issues and find expert-curated solutions for Python library errors.  
            - **🛠️ App Builder:**  Generate custom applications and workflows using pre-built templates and tools. *(Note: Disabled when "Llama Index" is selected.)*  
            - **🚀 GitHub Commit:**  Push the generated code to your existing GitHub repository. Easily commit the latest code changes without needing to manually copy or upload files.  
            - **🚪 Logout:**  Securely log out of your session to ensure your data and account remain protected.  

            ### 🚀 Ready to elevate your Python coding experience?  
            Navigate through the sidebar to get started!
            """)

            # Disable App Builder for Llama Index
    with st.sidebar:
        st.title(f"Welcome, {st.session_state.get('user_name', 'User')}")
        library = st.selectbox(
            "Choose a library to explore", 
            ["", "LangGraph", "LangChain", "Llama Index"],
            help="Choose a library to explore its features and functionality."
                )
        if library:
            st.session_state.library = library
        if library=='Llama Index':
            st.error("Llama Index is doesn't support App Builder.")
        if st.button("📖 How-to Guide"):
            st.session_state.current_page = 'how_to_guide'
            st.rerun()

        if st.button("🚨 Error Handling"):
            st.session_state.current_page = 'error_handling'
            st.rerun()
        
        if st.button("🛠️ App Builder",disabled=library=='Llama Index'):
            st.session_state.current_page = 'app_builder'
            st.rerun()
        
        if st.button("🚀 GitHub Commit"):
            st.session_state.current_page = 'githubcredentials'
            st.rerun()
        
        if st.button("🚪 Logout"):
            st.session_state.current_page = 'logout'
            st.rerun()
    
        if st.session_state.current_page == 'githubcredentials':
            st.markdown("---")
            st.subheader("Generate GitHub Personal Access Token (PAT)")
            st.markdown("""
            To generate a GitHub Personal Access Token (PAT), follow these steps:
            1. Visit [GitHub Token Settings](https://github.com/settings/tokens).
            2. Click on "Generate New Token."
            3. Select the permissions you need (e.g., "repo" for access to repositories).
            4. Click "Generate token."
            5. Copy and save the token (this is the only time you will see it).
            
            Use the token in the input field above when prompted for the PAT.
            """)
        
    
