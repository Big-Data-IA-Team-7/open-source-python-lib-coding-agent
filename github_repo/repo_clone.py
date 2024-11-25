import pandas as pd
import os
import git
import shutil
from pathlib import Path
from extract_code import extract_functions_from_repo

def clone_repo(repo_url, repo_dir):
    """Clone a GitHub repository."""

    if os.path.exists(repo_dir):
        shutil.rmtree(repo_dir)
    os.makedirs(repo_dir)
    git.Repo.clone_from(repo_url, repo_dir)

def process_github_repo(repo_url, repo_dir):
    """
    Clone a GitHub repository, extract Python functions, and create a DataFrame.
    """
    try:
        # Step 1: Clone the repository
        print("Cloning the repository...")
        clone_repo(repo_url, repo_dir)
        print("Repository cloned.")

        repo_dir_path = Path(repo_dir)

        # Step 2: Extract functions
        print("Extracting functions from the repository...")
        all_funcs = extract_functions_from_repo(repo_dir_path)
        if all_funcs is None:
            return None

        # Step 3: Create a DataFrame
        print("Creating DataFrame...")
        df = pd.DataFrame(all_funcs)
        return df
    finally:
        # Step 5: Cleanup - Remove the cloned repository directory
        print("Cleaning up cloned repository...")
        if os.path.exists(repo_dir):
            shutil.rmtree(repo_dir)
        print("Cleanup complete.")