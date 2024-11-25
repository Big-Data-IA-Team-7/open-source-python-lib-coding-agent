import os
import shutil
from pathlib import Path
import git
from extract_code import extract_structures_from_repo

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
        repo = git.Repo.clone_from(repo_url, repo_dir)
        print("Repository cloned successfully")
        return repo
    
    except git.exc.GitCommandError as e:
        print(f"Git clone failed: {e}")
        raise
    except PermissionError:
        print("Permission denied when creating or accessing directory")
        raise

def process_github_repo(repo_url, repo_dir):
    """
    Comprehensive GitHub repository processing function.
    
    Args:
        repo_url (str): URL of the GitHub repository
        repo_dir (str): Local directory to clone and process the repository
    
    Returns:
        DataFrame or None: Processed repository data
    """
    try:
        # Validate inputs
        if not repo_url or not repo_dir:
            print("Invalid repository URL or directory")
            return None

        # Clone repository
        try:
            clone_repo(repo_url, repo_dir)
        except (ValueError, git.exc.GitCommandError, PermissionError) as clone_error:
            print(f"Repository cloning failed: {clone_error}")
            return None

        # Convert to Path object for consistency
        repo_dir_path = Path(repo_dir)

        # Extract structures (assuming extract_structures_from_repo is defined elsewhere)
        try:
            print("Extracting structures from the repository...")
            results = extract_structures_from_repo(repo_dir_path)
            
            if results is None or len(results) == 0:
                print("No structures extracted from the repository")
                return None
            
            return results
        
        except Exception as extract_error:
            print(f"Error extracting structures: {extract_error}")
            return None

    except Exception as unexpected_error:
        print(f"Unexpected error in repository processing: {unexpected_error}")
        return None
    
    finally:
        # Cleanup - Always attempt to remove the repository directory
        try:
            if os.path.exists(repo_dir):
                shutil.rmtree(repo_dir)
                print("Cloned repository directory cleaned up")
        except Exception as cleanup_error:
            print(f"Error during cleanup: {cleanup_error}")