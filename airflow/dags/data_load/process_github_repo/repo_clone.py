import os
import shutil
from pathlib import Path
import git

def clone_repo(repo_url, repo_dir):
    """
    Clone a GitHub repository with basic error handling.

    Args:
        repo_url (str): URL of the GitHub repository to clone
        repo_dir (str): Local directory to clone the repository into

    Raises:
        ValueError: If repo_url is invalid
        git.exc.GitCommandError: If cloning fails
    """
    # Validate input
    if not repo_url or not isinstance(repo_url, str):
        raise ValueError("Invalid repository URL")
    
    # Ensure clean destination
    try:
        if os.path.exists(repo_dir):
            shutil.rmtree(repo_dir)
        os.makedirs(repo_dir, exist_ok=True)
        
        # Clone repository
        print(f"Cloning repository from {repo_url} to {repo_dir}")
        git.Repo.clone_from(repo_url, repo_dir)
        print("Repository cloned successfully")
        
        # Return the repository directory path as a string (JSON serializable)
        return repo_dir

    except git.exc.GitCommandError as e:
        print(f"Git clone failed: {e}")
        raise
    except PermissionError:
        print("Permission denied when creating or accessing directory")
        raise
