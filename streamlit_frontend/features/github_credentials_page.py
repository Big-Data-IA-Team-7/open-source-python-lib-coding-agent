import streamlit as st
from utils.github_credentials_updater import update_github_credentials

def github_credentials():

    if 'github_username' not in st.session_state:
        st.session_state.github_username = ""
    if 'github_token' not in st.session_state:
        st.session_state.github_token = ""

    st.title("GitHub Credentials")
    
    github_username = st.text_input("Enter the GitHub Username")
    github_token = st.text_input("Enter the GitHub Personal Access Token (PAT)", type="password")
    st.session_state.github_username = github_username
    st.session_state.github_token = github_token
    
    if st.button("Update GitHub Credentials"):
        if update_github_credentials(github_username, github_token):
            st.success("GitHub credentials updated successfully.")