import subprocess
import sys
import logging
import os
from typing import Tuple
import socket
import time

logger = logging.getLogger(__name__)

def find_next_available_port(start_port=8502, end_port=8510) -> int:
    """Find the next available port in our predefined range."""
    for port in range(start_port, end_port + 1):
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.bind(('0.0.0.0', port))
                logger.info(f"Found available port: {port}")
                return port
        except socket.error:
            continue
    raise RuntimeError("No ports available in the specified range")

def wait_for_port(port: int, host: str = '0.0.0.0', timeout: int = 30) -> bool:
    """Wait for a port to become available."""
    start_time = time.time()
    while True:
        if time.time() - start_time > timeout:
            return False
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                sock.settimeout(1)
                result = sock.connect_ex((host, port))
                if result == 0:
                    return True
        except:
            pass
        time.sleep(1)

def install_requirements(requirements_path: str) -> Tuple[bool, str]:
    """Install requirements from requirements.txt using pip."""
    try:
        if not os.path.exists(requirements_path):
            logger.error(f"Requirements file not found at {requirements_path}")
            return False, f"Requirements file not found at {requirements_path}"
            
        logger.info(f"Installing requirements from {requirements_path}")
        process = subprocess.run(
            [sys.executable, "-m", "pip", "install", "-r", requirements_path],
            capture_output=True,
            text=True,
            check=True
        )
        
        logger.info("Requirements installed successfully")
        return True, "Requirements installed successfully"
        
    except Exception as e:
        error_msg = f"Error installing requirements: {str(e)}"
        logger.error(error_msg)
        return False, error_msg

def launch_streamlit_app(frontend_path: str) -> Tuple[bool, str, int]:
    """Launch the Streamlit application."""
    try:
        if not os.path.exists(frontend_path):
            logger.error(f"Frontend file not found at {frontend_path}")
            return False, f"Frontend file not found at {frontend_path}", 0

        port = find_next_available_port()
        logger.info(f"Using port: {port}")
        
        # Construct the command with explicit host and port
        cmd = [
            "streamlit", "run", frontend_path,
            "--server.address", "0.0.0.0",
            "--server.port", str(port)
        ]
        
        logger.info(f"Launching Streamlit with command: {' '.join(cmd)}")
        
        # Launch the process
        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        # Wait for the port to become available
        if wait_for_port(port):
            logger.info(f"Streamlit app successfully launched on port {port}")
            return True, "Streamlit app launched successfully", port
        else:
            stderr = process.stderr.read() if process.stderr else "No error output available"
            logger.error(f"Streamlit failed to start: {stderr}")
            return False, f"Streamlit app failed to start: {stderr}", 0
            
    except Exception as e:
        error_msg = f"Failed to launch Streamlit app: {str(e)}"
        logger.error(error_msg)
        return False, error_msg, 0

def execute_application(requirements_path: str, frontend_path: str) -> Tuple[bool, int]:
    """Main function to execute the application setup and launch."""
    logger.info("Starting application execution")
    
    # Install requirements
    success, message = install_requirements(requirements_path)
    if not success:
        logger.error(f"Requirements installation failed: {message}")
        return False, 0
    
    # Launch the app
    success, message, port = launch_streamlit_app(frontend_path)
    if not success:
        logger.error(f"App launch failed: {message}")
        return False, 0
        
    logger.info(f"Application successfully launched on port {port}")
    return True, port