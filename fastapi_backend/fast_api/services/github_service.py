import subprocess
import os
from git import Repo
import requests
import shutil
from dotenv import load_dotenv

load_dotenv()

GITHUB_API_URL=os.getenv("GITHUB_API_URL")


# Function to validate GitHub credentials
def validate_github_credentials(username: str, token: str) -> str:
    try:
        # Test authentication using GitHub API
        response = requests.get(GITHUB_API_URL, auth=(username, token))
        if response.status_code == 200:
            return "Successfully logged in to GitHub!"
        elif response.status_code == 401:
            return "Invalid credentials. Please check your username or token."
        elif response.status_code == 403:
            return "No permission to access the repository. Please ensure you have the correct permissions."
        else:
            return f"Unexpected error: {response.status_code} - {response.json()}"
    except Exception as e:
        return f"An error occurred during validation: {e}"

def commit_and_push_changes(repo_path: str, repo_url: str, commit_message: str, token: str):
    """
    Commit and push the changes to GitHub repository.
    """
    try:
        # Commit the changes to the local repository
        repo = Repo(repo_path)
        repo.git.add(A=True)  # Stage all changes
        repo.index.commit(commit_message)  # Commit changes with the provided message

        # Push the changes to the GitHub repository (use token for authentication)
        origin = repo.remotes.origin
        origin.set_url(repo_url.replace("https://", f"https://{token}:x-oauth-basic@"))  # Set the remote URL with token
        origin.push()

        # Return a success message if commit and push were successful
        return {"message": "Files successfully committed and pushed to GitHub."}

    except Exception as e:
        # Log or print the error and raise a generic exception with a message
        return {"error": f"Error committing and pushing files: {str(e)}"}

def copy_files_to_repo(folder_path: str, repo_path: str):
    """
    Copy files from the specified folder to the cloned repo, maintaining the directory structure.
    """
    try:
        # Traverse the source folder and replicate the structure in the destination
        for root, dirs, files in os.walk(folder_path):
            # Compute the relative path of the current directory from the source folder
            relative_dir = os.path.relpath(root, folder_path)
            dest_dir = os.path.join(repo_path, relative_dir)

            # Create the destination directory if it doesn't exist
            if not os.path.exists(dest_dir):
                os.makedirs(dest_dir)

            # Copy each file in the current directory to the destination directory
            for file_name in files:
                src_file = os.path.join(root, file_name)
                dest_file = os.path.join(dest_dir, file_name)
                shutil.copy2(src_file, dest_file)  # copy2 to preserve metadata

        return {"message": "Files and folders successfully copied to the repository."}
    
    except Exception as e:
        print(f"Error copying files and folders: {str(e)}")
        return {"error": f"Error copying files and folders: {str(e)}"}