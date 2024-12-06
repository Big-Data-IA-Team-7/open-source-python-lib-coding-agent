import os
import streamlit as st
import requests
import logging

from utils.chat_helpers import process_stream

logger = logging.getLogger(__name__)
FAST_API_URL = os.getenv("FAST_API_URL")

def stream_code_generation(query: str, history: list):
    """
    Stream code generation from the API endpoint and process the response.
    
    Args:
        query: The user's query
        history: List of previous chat messages
    Returns:
        str: The complete response if successful, None if errors occur
    """
    payload = {
        "query": query,
        "history": history
    }

    headers = {
        "Accept": "text/event-stream",
        "Authorization": f"Bearer {st.session_state['token']}"
    }
    
    full_response = ""  # Initialize before the loop
    
    try:
        with requests.post(
            f"{FAST_API_URL}/chat/generate-code",
            json=payload,
            headers=headers,
            stream=True
        ) as response:
            response.raise_for_status()
            
            for line in response.iter_lines():
                if line:
                    decoded_line = line.decode('utf-8')
                    chunk_response = process_stream(decoded_line)
                    if chunk_response:
                        full_response = chunk_response  # Update the full response
        return full_response  # Return the final complete response
        
    except requests.exceptions.RequestException as e:
        logger.error(f"API request failed: {str(e)}")
        st.error(f"API request failed: {str(e)}")
        return None
        
    except Exception as e:
        logger.error(f"An unexpected error occurred: {str(e)}")
        st.error(f"An unexpected error occurred: {str(e)}")
        return None

def stream_error_handling(task: str, code: str, error: str, history: list):
    """
    Stream code generation from the API endpoint and process the response.
    
    Args:
        task: The task described by the user
        code: The code that was executed
        error: The error that occured in the given code
        history: List of previous chat messages
    Returns:
        str: The complete response if successful, None if errors occur
    """
    payload = {
        "task": task,
        "code": code,
        "error": error,
        "history": history
    }

    headers = {
        "Accept": "text/event-stream",
        "Authorization": f"Bearer {st.session_state['token']}"
    }
    
    full_response = ""  # Initialize before the loop
    
    try:
        with requests.post(
            f"{FAST_API_URL}/chat/handle-error",
            json=payload,
            headers=headers,
            stream=True
        ) as response:
            response.raise_for_status()
            
            for line in response.iter_lines():
                if line:
                    decoded_line = line.decode('utf-8')
                    chunk_response = process_stream(decoded_line)
                    if chunk_response:
                        full_response = chunk_response  # Update the full response
                        
        return full_response  # Return the final complete response
        
    except requests.exceptions.RequestException as e:
        logger.error(f"API request failed: {str(e)}")
        st.error(f"API request failed: {str(e)}")
        return None
        
    except Exception as e:
        logger.error(f"An unexpected error occurred: {str(e)}")
        st.error(f"An unexpected error occurred: {str(e)}")
        return None