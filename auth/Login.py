import streamlit as st
import requests
from dotenv import load_dotenv
import os
from requests.exceptions import RequestException

# Load environment variables from .env file
load_dotenv()

# Get the API URL from the environment variables
FAST_API_URL = os.getenv("FAST_API_URL")

def login():
    try:
        # Add a back button at the top
        if st.button("← Back", type="secondary"):
            st.session_state.current_page = 'landing'
            st.rerun()
            
        st.title("🐍 Python Library Coding Agent")
        st.header('Login')

        # Initialize session states
        if 'token' not in st.session_state:
            st.session_state.token = None
        if 'user_name' not in st.session_state:
            st.session_state.user_name = None

        with st.form(key='login_form'):
            username = st.text_input('**Username**', placeholder='Enter your username')
            password = st.text_input('**Password**', type='password', placeholder='Enter your password')
            submit_button = st.form_submit_button(label='Login')

            if submit_button:
                # Validate inputs before making API call
                validation_errors = []

                if not username:
                    validation_errors.append("Username is required")

                if not password:
                    validation_errors.append("Password is required")

                # If there are validation errors, display them and stop
                if validation_errors:
                    for error in validation_errors:
                        st.error(error)
                    return
                
                # Create a placeholder for messages
                message_placeholder = st.empty()

                # If validation passes, proceed with API call
                try:
                    # Show spinner while making API request
                    with message_placeholder, st.spinner('Logging in...'):
                        payload = {
                            "username": username,
                            "password": password
                        }
                        response = requests.post(
                            f"{FAST_API_URL}/auth/login", 
                            json=payload,
                            timeout=10
                        )

                    # Clear spinner
                    message_placeholder.empty()

                    if response.status_code == 200:
                        try:
                            data = response.json()
                            token = data.get("access_token")
                            username = data.get("username")
                            
                            if token and username:
                                st.success("User Logged in Successfully")
                                st.session_state.token = token
                                st.session_state.user_name = username
                                # Set logged_in state to True
                                st.session_state.logged_in = True
                                # Navigate to code generation page
                                st.session_state.current_page = 'code_generation'
                                st.rerun()
                            else:
                                st.error("Invalid response from server. Missing token or username.")
                                
                        except ValueError:
                            st.error("Invalid response format from server")
                            
                    elif response.status_code == 400:
                        error_data = response.json()
                        error_message = error_data.get('detail', 'Invalid Credentials')
                        st.error(error_message)
                    elif response.status_code == 401:
                        st.error("Unauthorized. Please check your credentials.")
                    elif response.status_code == 404:
                        st.error("User not found. Please register first.")
                    else:
                        st.error(f"Login failed (Status code: {response.status_code}). Please try again later.")

                except RequestException as e:
                    st.error("Connection error: Unable to reach the server. Please try again later.")
                except Exception as e:
                    st.error("An unexpected error occurred during login. Please try again.")

    except Exception as e:
        st.error("Something went wrong with the login page. Please refresh and try again.")
        if st.button("Refresh Page"):
            st.rerun()