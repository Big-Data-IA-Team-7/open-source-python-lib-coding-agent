import subprocess
import sys
import logging
import os
from typing import Tuple
import streamlit as st

logger = logging.getLogger(__name__)

def install_requirements(requirements_path: str) -> Tuple[bool, str]:
    """
    Install requirements from requirements.txt using pip.
    
    Args:
        requirements_path: Path to requirements.txt file
        
    Returns:
        Tuple of (success_bool, message_str)
    """
    try:
        # Check if requirements file exists
        if not os.path.exists(requirements_path):
            return False, f"Requirements file not found at {requirements_path}"
            
        # Install requirements using pip
        process = subprocess.run(
            [sys.executable, "-m", "pip", "install", "-r", requirements_path],
            capture_output=True,
            text=True,
            check=True
        )
        
        return True, "Requirements installed successfully"
        
    except subprocess.CalledProcessError as e:
        error_msg = f"Failed to install requirements: {e.stderr}"
        logger.error(error_msg)
        return False, error_msg
    except Exception as e:
        error_msg = f"Unexpected error installing requirements: {str(e)}"
        logger.error(error_msg)
        return False, error_msg

def launch_streamlit_app(frontend_path: str) -> Tuple[bool, str]:
    """
    Launch the Streamlit application.
    
    Args:
        frontend_path: Path to the frontend.py file
        
    Returns:
        Tuple of (success_bool, message_str)
    """
    try:
        # Check if frontend file exists
        if not os.path.exists(frontend_path):
            return False, f"Frontend file not found at {frontend_path}"
            
        # Launch streamlit app in a new process
        process = subprocess.Popen(
            ["streamlit", "run", frontend_path],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        # Wait a short time to check for immediate failures
        try:
            process.wait(timeout=2)
            if process.returncode is not None and process.returncode != 0:
                stderr = process.stderr.read()
                return False, f"Streamlit app failed to start: {stderr}"
        except subprocess.TimeoutExpired:
            # Process didn't exit within timeout - this is good!
            # It means the app is probably running
            pass
            
        return True, "Streamlit app launched successfully"
        
    except Exception as e:
        error_msg = f"Failed to launch Streamlit app: {str(e)}"
        logger.error(error_msg)
        return False, error_msg

def execute_application(requirements_path: str, frontend_path: str) -> None:
    """
    Main function to execute the application setup and launch.
    
    Args:
        requirements_path: Path to requirements.txt file
        frontend_path: Path to frontend.py file
    """
    # First install requirements
    success, message = install_requirements(requirements_path)
    if not success:
        st.error(message)
        return
    
    st.success("Requirements installed successfully")
    
    # Then launch the streamlit app
    success, message = launch_streamlit_app(frontend_path)
    if not success:
        st.error(message)
        return
        
    st.success("Application launched successfully!")
    st.info("You can access the application in your browser")