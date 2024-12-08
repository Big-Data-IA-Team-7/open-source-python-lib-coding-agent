import streamlit as st
import requests
import os 
from dotenv import load_dotenv
# Load environment variables from .env file
load_dotenv()

# Get the API URL from the environment variables
FAST_API_URL = os.getenv("FAST_API_URL")

def github_commit_app():
    """Streamlit interface for automating GitHub commit, push, and cleanup."""
    st.title("Automated GitHub Commit App with Cleanup")

    # Input fields
    repo_url = st.text_input("Enter GitHub Repository URL")
    file_name = st.text_input("File Name (e.g., app.py)")
    commit_message = st.text_input("Commit Message")
    code_content = st.text_area("Write or edit your code below:", height=300, value="# Your Python code here\n")

    if st.button("Save, Commit, and Push"):
        if not repo_url or not file_name or not commit_message or not code_content:
            st.error("Please fill in all fields.")
        else:
            with st.spinner("Processing..."):
                # API request payload
                payload = {
                    "repo_url": repo_url,
                    "file_name": file_name,
                    "commit_message": commit_message,
                    "code_content": code_content,
                }

                try:
                    # Send the request to the FastAPI backend
                    response = requests.post(
                            f"{FAST_API_URL}/github/process-repo/", 
                            json=payload,
                            timeout=10
                        )
                    if response.status_code == 200:
                        result = response.json()
                        st.success(result["commit_status"])
                        st.info(result["cleanup_status"])
                    else:
                        st.error(f"Error: {response.json()['detail']}")
                except Exception as e:
                    st.error(f"An error occurred: {str(e)}")

