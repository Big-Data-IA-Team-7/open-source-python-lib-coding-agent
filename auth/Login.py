import streamlit as st
import requests
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

# Get the API URL from the environment variables
FAST_API_URL = os.getenv("FAST_API_URL")

def login():
    st.title('Open Source Code Agent')
    st.header('Login')

    if 'logging_in' not in st.session_state:
        st.session_state.logging_in = False
    if 'tokem' not in st.session_state:
        st.session_state.token = None
    if 'User_name' not in st.session_state:
        st.session_state.User_name = None

    with st.form(key='login_form'):
        email = st.text_input('Enter the EmailID',placeholder='Enter your emailID')
        password = st.text_input('Enter the Password', type='password',placeholder='Enter your password')
        submit_button = st.form_submit_button(label='Login')

        if submit_button:
            payload = {
                "useremail": email,
                "password": password
            }
            response = requests.post(f"{FAST_API_URL}/auth/login", json=payload)

            if response.status_code == 200:
                data=response.json()
                token = data.get("access_token")
                username=data.get("username")
                st.success("User Logged in Successfully")
                st.session_state.logging_in = True
                st.session_state.token = token
                st.session_state.User_name = username
                st.rerun()
            elif response.status_code == 400:
                st.error('Invlid Credentials')
            else:
                st.error('Something went wrong. Please try again later.')