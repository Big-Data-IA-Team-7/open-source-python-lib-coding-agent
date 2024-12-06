import streamlit as st
import requests
import os
import time
import logging
from requests.exceptions import RequestException

from utils.validate_fields import is_valid_username, is_valid_email, is_valid_password

# Get the API URL from the environment variables
FAST_API_URL = os.getenv("FAST_API_URL")

def register_user():
    logger = logging.getLogger(__name__)
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
                        logger.error(error)
                        st.error(error)
                    return

                # Create placeholder for messages
                message_placeholder = st.empty()
                
                # If validation passes, proceed with API call
                try:
                    # Show spinner during API call
                    with message_placeholder, st.spinner('Registering user...'):
                        payload = {
                            "username": username,
                            "email": email,
                            "password": password
                        }
                        response = requests.post(
                            f"{FAST_API_URL}/auth/register", 
                            json=payload,
                            timeout=10
                        )

                    # Clear spinner and show appropriate message
                    message_placeholder.empty()

                    if response.status_code == 201:
                        # Show success message
                        logger.info("✅ Registration Successful!")
                        st.success("✅ Registration Successful!")
                        
                        # Show redirecting message with countdown
                        countdown_placeholder = st.empty()
                        for seconds in range(3, 0, -1):
                            countdown_placeholder.info(f"Redirecting to login page in {seconds} seconds...")
                            time.sleep(1)
                        countdown_placeholder.empty()
                        
                        # Redirect to login
                        st.session_state.current_page = 'login'
                        st.rerun()
                            
                    elif response.status_code == 400:
                        error_data = response.json()
                        error_message = error_data.get('detail', 'User Already Exists')
                        logger.error(error_message)
                        st.error(error_message)
                    else:
                        logger.error("Registration failed. Please try again later.")
                        st.error("Registration failed. Please try again later.")

                except RequestException as e:
                    logger.error(f"Connection error: Unable to reach the server. Please try again later.")
                    st.error(f"Connection error: Unable to reach the server. Please try again later.")
                except Exception as e:
                    logger.error("An unexpected error occurred. Please try again.")
                    st.error("An unexpected error occurred. Please try again.")
                    
    except Exception as e:
        logger.error("Something went wrong with the registration page. Please refresh and try again.")
        st.error("Something went wrong with the registration page. Please refresh and try again.")
        if st.button("Refresh Page"):
            st.rerun()