import streamlit as st
import requests 
from dotenv import load_dotenv
import os
from requests.exceptions import RequestException
from validate_fields import is_valid_username, is_valid_email, is_valid_password

# Load environment variables from .env file
load_dotenv()

# Get the API URL from the environment variables
FAST_API_URL = os.getenv("FAST_API_URL")

def register_user():
    try:
        # Add back button at the top
        if st.button("← Back", type="secondary"):
            st.session_state.current_page = 'landing'
            st.rerun()

        st.title("🐍 Python Library Coding Agent")
        st.header('Register')

        # Add helper text for requirements
        with st.expander("Registration Requirements"):
            st.markdown("""
            **Username Requirements:**
            - 3-20 characters long
            - Must start with a letter
            - Can contain letters, numbers, underscores, and hyphens
            
            **Password Requirements:**
            - Minimum 8 characters
            - At least one uppercase letter
            - At least one lowercase letter
            - At least one number
            - At least one special character
            
            **Email Requirements:**
            - Must be a valid email format
            - Example: user@domain.com
            """)

        with st.form(key='register_form'):
            username = st.text_input('**Username**', placeholder='Enter your username')
            email = st.text_input('**Email**', placeholder='Enter your email')
            password = st.text_input('**Password**', type='password', placeholder='Enter your password')
            submit_button = st.form_submit_button(label='Register')

            if submit_button:
                # Validate all inputs before making API call
                validation_errors = []

                if not username:
                    validation_errors.append("Username is required")
                elif not is_valid_username(username):
                    validation_errors.append("Invalid username format")

                if not email:
                    validation_errors.append("Email is required")
                elif not is_valid_email(email):
                    validation_errors.append("Invalid email format")

                if not password:
                    validation_errors.append("Password is required")
                else:
                    is_password_valid, password_message = is_valid_password(password)
                    if not is_password_valid:
                        validation_errors.append(password_message)

                # If there are validation errors, display them and stop
                if validation_errors:
                    for error in validation_errors:
                        st.error(error)
                    return

                # If validation passes, proceed with API call
                try:
                    payload = {
                        "username": username,
                        "email": email,
                        "password": password
                    }
                    response = requests.post(
                        f"{FAST_API_URL}/auth/register", 
                        json=payload,
                        timeout=10  # Add timeout to prevent hanging
                    )

                    if response.status_code == 200:
                        st.success("User Registered Successfully")
                        # Redirect to login page after successful registration
                        st.session_state.current_page = 'login'
                        st.rerun()
                    elif response.status_code == 400:
                        error_data = response.json()
                        error_message = error_data.get('detail', 'User Already Exists')
                        st.error(error_message)
                    else:
                        st.error("Registration failed. Please try again later.")

                except RequestException as e:
                    st.error(f"Connection error: Unable to reach the server. Please try again later.")
                except Exception as e:
                    st.error("An unexpected error occurred. Please try again.")
                    
    except Exception as e:
        st.error("Something went wrong with the registration page. Please refresh and try again.")
        if st.button("Refresh Page"):
            st.rerun()