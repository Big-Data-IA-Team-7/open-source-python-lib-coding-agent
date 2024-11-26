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
        
        # Show success message
        st.sidebar.success("Logged out successfully!")
        
        # Force page rerun to update UI
        st.rerun()
        
    except Exception as e:
        st.sidebar.error(f"Error during logout: {str(e)}")
        # Still try to rerun even if there's an error
        st.rerun()