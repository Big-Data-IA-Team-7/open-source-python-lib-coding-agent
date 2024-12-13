import streamlit as st
import traceback
from utils.api_helpers import stream_application_build
import logging
from pathlib import Path
from utils.app_launcher import execute_application
import threading
import requests
import os

FAST_API_URL = os.getenv("FAST_API_URL")

@st.fragment
def launch_application():
    st.button("🚀 Launch Application", on_click=run_app_in_thread, type="primary")
    st.info("Click the button above to start the application in a new window")

@st.fragment
def commit_to_github(folder_path: str):
    repo_url = st.text_input("Enter repository URL for GitHub:")
    commit_message = st.text_input("Commit Message")
    if st.button("🚀 Commit and Push", type="secondary"):
        
        response = requests.get(f"{FAST_API_URL}/git/check-github-credentials/{st.session_state.user_name}")
        
        if response.status_code == 200:
            output = response.json()
            if output.get("message") == "User has valid GitHub credentials.":
                st.session_state.github_username = output.get("github_username")
                st.session_state.github_token = output.get("github_token")
                st.success("Github credentials found.")

                # Commit and Push Button
                with st.spinner("Committing and pushing changes..."):
                    # Package the input data in the correct structure
                    repo_details = {
                        "repo_url": repo_url,
                        "commit_message": commit_message,
                        "folder_path": folder_path
                    }

                    credentials = {
                        "username": st.session_state.github_username,
                        "token": st.session_state.github_token
                    }
                    response = requests.post(f"{FAST_API_URL}/git/commit-and-push/", json={
                        "repo_details": repo_details,
                        "credentials": credentials
                    })
                    
                    commit_result = response.json()
                    if "message" in commit_result:
                        st.success("Code committed and pushed successfully!")
                    else:
                        st.error(f"Unexpected response: {commit_result}")
        
            elif output.get("message") == "User does not have GitHub credentials.":
                st.warning("GitHub credentials not found. Please go to the GitHub page to set up your username and Personal Access Token (PAT) first.")

def run_app_in_thread():
    """Execute the application in a separate thread."""
    def run():
        execute_application("requirements.txt", "frontend.py")
    
    thread = threading.Thread(target=run, daemon=True)
    thread.start()

def code_generation_interface():
    logger = logging.getLogger(__name__)
    try:
        # Error handling for session state initialization
        if 'build_stage' not in st.session_state:
            st.session_state['build_stage'] = None
        if 'stage_content' not in st.session_state:
            st.session_state['stage_content'] = {}
        if 'last_error_cg' not in st.session_state:
            st.session_state['last_error_cg'] = None
        if 'final_output' not in st.session_state:
            st.session_state['final_output'] = False
        if 'token' not in st.session_state:
            st.error("Please log in first")
            return

        st.title("🛠️ App Builder")
        
        st.markdown("""
        Build a complete LangGraph application using Streamlit for your usecase. Try an example or enter your own requirements below:
        """)

        # Example cards in columns
        col1, col2 = st.columns(2)
        example1 = "Create a LangGraph application for a Code Generation Assistant that can understand programming requirements, generate code with proper documentation, handle edge cases, and provide explanations for the implementation."
        example2 = "Build a LangGraph application for a PDF-based RAG agent that can process PDF documents, extract relevant information, create embeddings, handle semantic search, and provide contextual responses with source citations."

        with col1:
            if st.button("📟 Code Generation Assistant", help=example1, use_container_width=True):
                st.session_state['user_input'] = example1
                
        with col2:
            if st.button("📄 PDF-based RAG Agent", help=example2, use_container_width=True):
                st.session_state['user_input'] = example2

        # Main input
        user_input = st.text_area("Enter your application requirements:", 
                                 value=st.session_state.get('user_input', ''),
                                 height=100)

        # Build button
        if st.button("🚀 Build Application", type="primary", use_container_width=True):
            if not user_input:
                st.error("Please enter your requirements first!")
                return
                
            # Reset states for new build
            st.session_state['build_stage'] = 'starting'
            st.session_state['stage_content'] = {}
            
            try:
                # Define stage messages
                stage_messages = {
                    'create_app_research_plan': '🔍 Researching and gathering relevant implementation details...',
                    'conduct_research': '👨‍💻 Building application components...',
                    'build_app': '⚡ Evaluating code quality and performance...',
                    'evaluate_code': '📦 Generating project dependencies...',
                    'generate_requirements_txt': '📝 Creating project documentation...'
                }
                
                # Create a single persistent container for progress messages
                progress_container = st.empty()
                
                # Show initial status
                progress_container.info("🤔 Planning application architecture and steps...")
                
                # Define the progress update function
                def update_progress(chunk_type):
                    """Update progress message based on chunk type"""
                    if chunk_type in stage_messages:
                        progress_container.info(stage_messages[chunk_type])
                
                # Store the update function in session state
                st.session_state['update_progress'] = update_progress
                
                # Get the streaming response
                full_response = stream_application_build(user_input, [])
                
                # Clear progress message after completion
                progress_container.empty()
                
                if full_response:
                    success_container = st.success("✅ Application built successfully!")
                    
                    # Check if required files exist and add launch button
                    if Path("requirements.txt").exists() and Path("frontend.py").exists():
                        launch_application()

                        generated_app_path = str(Path("generated_app").absolute())
                        
                        # Store the app files in session state
                        try:
                            # GitHub commit section
                            commit_to_github(generated_app_path)
                        except Exception as e:
                            logger.error(f"Error processing app data: {str(e)}")
                            st.error(f"Error processing application data: {str(e)}")
                else:
                    st.error("❌ Failed to build application")
                    
            except Exception as build_error:
                logger.error(f"Build error: {str(build_error)}")
                st.error(f"An error occurred during the build process: {str(build_error)}")
                st.session_state['last_error_cg'] = {
                    'type': type(build_error).__name__,
                    'message': str(build_error),
                    'traceback': traceback.format_exc()
                }

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