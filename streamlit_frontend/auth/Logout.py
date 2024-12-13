import streamlit as st
from typing import NoReturn
import logging

def logout() -> NoReturn:
    logger = logging.getLogger(__name__)
    """
    Handles user logout by clearing session state and redirecting.
    
    Clears all authentication-related session state variables and 
    displays logout confirmation message.
    """
    try:
        # Clear all authentication-related session state
        for key in ['logged_in', 'token', 'user_name']:
            if key in st.session_state:
                del st.session_state[key]
        
        # Reset current page to landing
        st.session_state.current_page = 'landing'
            
    except Exception as e:
        logger.error(f"Error during logout: {str(e)}")
        st.error(f"Error during logout: {str(e)}")
        
        # Add a refresh button in case of error
        if st.button("Refresh Page"):
            st.rerun()