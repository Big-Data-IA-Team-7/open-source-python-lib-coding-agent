import streamlit as st
import requests 
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

# Get the API URL from the environment variables
FAST_API_URL = os.getenv("FAST_API_URL")


def register_user():
    st.title('Open Souce Code Agent')
    st.header('Register')

    with st.form(key='register_form'):
        username = st.text_input('Enter Username')
        email = st.text_input('Enter the EmailID')
        password = st.text_input('Enter the Password', type='password')
        submit_button = st.form_submit_button(label='Register')

        if submit_button:
            payload={
                "username":username,
                "email":email,
                "password":password
            }
            response = requests.post(f"{FAST_API_URL}/auth/register", json=payload)

            if response.status_code == 200:
                st.success("User Registered Successfully")
            elif response.status_code == 400:
                st.error("User Already Exists")
            else:    
                st.error("Something went wrong. Please try again later.")
                st.write(f"Response content: {response.text}")
                
        