import streamlit as st
import requests
import os
from dotenv import load_dotenv
import time
import openai
load_dotenv()

# FastAPI Backend URL (from environment variable)
FAST_API_URL = os.getenv("FAST_API_URL")
openai.api_key = os.getenv("OPENAI_API_KEY")

# Function to display Streamlit UI for GitHub authentication and repository management
def github_repo_management():
    #From here the github start
    st.title("GitHub Authentication and Repository Management")
    st.subheader("Repository Details")
    repo_url = st.text_input("Enter GitHub Repository URL")
    commit_message = st.text_input("Commit Message")
    # Commit and Push Button
    if st.button("Commit and Push"):
        with st.spinner("Committing and pushing changes..."):
            # Package the input data in the correct structure
            repo_details = {
                "repo_url": repo_url,
                "commit_message": commit_message,
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
    
    # if st.button("← Back", type="secondary"):
    #         st.session_state.current_page = 'code_generation'
    #         st.rerun()



