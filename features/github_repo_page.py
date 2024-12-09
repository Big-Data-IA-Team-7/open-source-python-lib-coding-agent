import streamlit as st
import requests
import os
from dotenv import load_dotenv
import time
import openai
load_dotenv()

# FastAPI Backend URL (from environment variable)
FAST_API_URL = os.getenv("FAST_API_URL")
openai.api_key = os.getenv("OPENAI_API_KEY")

# Function to display Streamlit UI for GitHub authentication and repository management
def github_repo_management():
    #Dummy LLM (We will remove this part with actual code generation)
    PROMPT = "Create a Streamlit app for user login with fields for username and password, and a login button."
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": PROMPT}
            ],
            max_tokens=300,
            temperature=0.7,
        )

        # Print the entire response to debug the structure
        st.write(response)

        # Check if 'choices' is in the response and has content
        if "choices" in response and len(response['choices']) > 0:
            generated_text = response.choices[0].message['content'].strip()

            # Extract the Python code block (ignoring any instructions)
            if "```python" in generated_text and "```" in generated_text:
                # Find the code block
                start_index = generated_text.find("```python") + len("```python")
                end_index = generated_text.find("```", start_index)
                code_content = generated_text[start_index:end_index].strip()

                # Assign the file name (you can set any name or infer from the prompt)
                file_name = "login_app.py"

                # Save the file name and code content in the session state
                st.session_state.file_name = file_name
                st.session_state.code_content = code_content
            else:
                st.error("No Python code found in the response.")
        else:
            st.error("Unexpected response format from OpenAI API.")
    except Exception as e:
        st.error(f"Error generating code: {e}")

    #From here the github start
    st.title("GitHub Authentication and Repository Management")
    st.subheader("Repository Details")
    repo_url = st.text_input("Enter GitHub Repository URL")
    commit_message = st.text_input("Commit Message")
    # Commit and Push Button
    if st.button("Commit and Push"):
        with st.spinner("Committing and pushing changes..."):
            # Package the input data in the correct structure
            repo_details = {
                "repo_url": repo_url,
                "commit_message": commit_message,
                "file_name": file_name,
                "code_content": code_content
            }

            credentials = {
                "username": st.session_state.github_username,
                "token": st.session_state.github_token
            }
            response = requests.post(f"{FAST_API_URL}/git/commit-and-push/", json={
                "repo_details": repo_details,
                "credentials": credentials
            })
            
            commit_result = response.json()
            st.write(f"Commit result: {commit_result}")  # Show the entire result for debugging
            if "message" in commit_result:
                st.success("Code committed and pushed successfully!")
            else:
                st.error(f"Unexpected response: {commit_result}")

    if st.button("← Back", type="secondary"):
            st.session_state.current_page = 'code_generation'
            st.rerun()



