import streamlit as st
import os 
import requests
from dotenv import load_dotenv
import time 
import logging
load_dotenv()
FAST_API_URL = os.getenv("FAST_API_URL")

def github_credentials():
    st.title("GitHub Credentials")
    response = requests.get(f"{FAST_API_URL}/git/check-github-credentials/{st.session_state.user_name}")
    
    if response.status_code == 200:
        output = response.json()
        if output.get("message") == "User has valid GitHub credentials.":
            github_username=output.get("github_username")
            github_token=output.get("github_token")
            st.session_state.github_username = github_username
            st.session_state.github_token = github_token
            st.success("Github credentials found. You can update them if necessary.")
            with st.spinner("redirecting to the Github Repository Management Page"):
                    time.sleep(3)
                    # Redirect to github page
                    st.session_state.current_page = "github"
                    st.rerun()
        elif output.get("message") == "User does not have GitHub credentials.":
            st.error("No GitHub credentials found. You can add them below.")
            github_username = st.text_input("Enter the GitHub Username")
            github_token = st.text_input("Enter the GitHub Personal Access Token (PAT)", type="password")
            st.session_state.github_username = github_username
            st.session_state.github_token = github_token
            if st.button("Update GitHub Credentials"):
                url = f"{FAST_API_URL}/git/update-github-credentials/{st.session_state.user_name}"
                payload = {
                    "username": st.session_state.user_name,
                    "github_username": github_username,
                    "git_token": github_token
                }
                response = requests.put(url, json=payload)
                if response.status_code == 200:
                    result = response.json()
                    if "message" in result:
                        st.success(result["message"])
                        with st.spinner("redirecting to the Github Repository Management Page"):
                            time.sleep(3)
                            # Redirect to github page
                            st.session_state.current_page = "github"
                            st.rerun()
                    else:
                        st.error("Unexpected response.")
                else:
                    st.error("Failed to update GitHub credentials.")
        elif output.get("message") == "User not found in the database.":
            st.error("User does not exist.")
        else:
            st.error("Unexpected response.")
   # Sidebar for GitHub Personal Access Token (PAT) generation
    st.sidebar.subheader("Generate GitHub Personal Access Token (PAT)")
    st.sidebar.markdown("""
    To generate a GitHub Personal Access Token (PAT), follow these steps:
    1. Visit [GitHub Token Settings](https://github.com/settings/tokens).
    2. Click on "Generate New Token."
    3. Select the permissions you need (e.g., "repo" for access to repositories).
    4. Click "Generate token."
    5. Copy and save the token (this is the only time you will see it).
    
    Use the token in the input field above when prompted for the PAT.
    """)