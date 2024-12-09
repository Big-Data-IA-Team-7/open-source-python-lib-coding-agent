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

# Function to commit and push code to GitHub using token and username
def commit_and_push(repo_path: str, commit_message: str, username: str, token: str, repo_owner: str, file_name: str, code_content: str = None) -> str:
    try:
        # Initialize the repository
        repo = Repo(repo_path)

        # If code_content is provided, write the content to the specified file
        if code_content and file_name:
            with open(os.path.join(repo_path, file_name), "w") as f:
                f.write(code_content)
        
        # Stage the specific file (if provided) or all changes
        if file_name:
            repo.git.add(file_name)
        else:
            repo.git.add(A=True)

        # Commit changes
        repo.index.commit(commit_message)

        # Correct the remote URL with the actual GitHub repository owner
        remote_url = f"https://{username}:{token}@github.com/{repo_owner}/{repo_path.split('/')[-1]}.git"

        # Set the remote URL for the repository
        repo.remotes.origin.set_url(remote_url)

        # Push to remote repository
        result = subprocess.run(['git', 'push'], cwd=repo_path, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        if result.returncode == 0:
            # If push is successful, delete the local files
            shutil.rmtree(repo_path)
            return "Changes committed and pushed successfully! Local repository has been deleted."
        else:
            return f"An error occurred while pushing: {result.stderr.decode()}"
    except Exception as e:
        return f"An error occurred during commit and push: {e}"
