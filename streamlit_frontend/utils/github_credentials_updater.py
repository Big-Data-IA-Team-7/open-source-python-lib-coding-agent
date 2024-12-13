import streamlit as st
import os
import requests

FAST_API_URL = os.getenv("FAST_API_URL")

def update_github_credentials(github_username, github_token):
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
            return True
        else:
            st.error("Unexpected response.")
            return False
    else:
        st.error("Failed to update GitHub credentials.")
        return False