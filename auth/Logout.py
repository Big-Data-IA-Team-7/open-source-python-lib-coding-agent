import streamlit as st
from typing import NoReturn

def logout() -> NoReturn:
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
        st.error(f"Error during logout: {str(e)}")
        
        # Add a refresh button in case of error
        if st.button("Refresh Page"):
            st.rerun()