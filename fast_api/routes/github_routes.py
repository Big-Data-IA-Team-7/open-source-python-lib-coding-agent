from fastapi import APIRouter, HTTPException
from git import Repo
import os
from fast_api.schema.request_schema import GitHubCredentials, RepoDetails, GitHubCredentialsRequest
from fast_api.services.github_service import validate_github_credentials,commit_and_push_changes,copy_files_to_repo
from fast_api.config.db_connection import snowflake_connection
import logging
import shutil

logger = logging.getLogger(__name__)
router = APIRouter()

@router.get("/check-github-credentials/{username}")
async def check_github_credentials(username: str):
    try:
        # Establish Snowflake connection
        conn = snowflake_connection()
        cursor = conn.cursor()

        # Query to check if the user has GitHub credentials
        check_query = """
        SELECT githubusername, gittoken
        FROM USERDETAILSGithub
        WHERE username = %s
        """
        cursor.execute(check_query, (username,))
        result = cursor.fetchone()

        if result:
            github_username, git_token = result

            # Check if credentials exist
            if github_username is not None and git_token is not None:
                return {
                    "message": "User has valid GitHub credentials.",
                    "github_username": github_username,
                    "github_token": git_token
                }
            else:
                return {"message": "User does not have GitHub credentials."}
        else:
            return {"message": "User not found in the database."}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error checking GitHub credentials: {str(e)}")
    
    finally:
        cursor.close()
        conn.close()


@router.put("/update-github-credentials/{username}")
async def update_github_credentials(username: str, credentials: GitHubCredentialsRequest):
    try:
        # Establish Snowflake connection
        conn = snowflake_connection()
        cursor = conn.cursor()

        # # Hash the GitHub token before saving it
        # hashed_token = token_hashing(credentials.git_token)

        # Check if the user already exists in the database
        check_query = """
        SELECT COUNT(*) 
        FROM USERDETAILSGithub
        WHERE username = %s
        """
        cursor.execute(check_query, (username,))
        user_exists = cursor.fetchone()[0]

        if user_exists:
            # Update GitHub credentials if they exist
            update_query = """
            UPDATE USERDETAILSGithub
            SET githubusername = %s, gittoken = %s
            WHERE username = %s
            """
            cursor.execute(update_query, (credentials.github_username, credentials.git_token, username))
            conn.commit()
            return {"message": "GitHub credentials updated successfully."}
        else:
            # Insert new credentials if the user does not exist
            insert_query = """
            INSERT INTO USERDETAILSGithub (username, githubusername, gittoken)
            VALUES (%s, %s, %s)
            """
            cursor.execute(insert_query, (username, credentials.github_username, credentials.git_token))
            conn.commit()
            return {"message": "GitHub credentials added successfully."}

    except Exception as e:
        logger.error(f"Error updating GitHub credentials for {username}: {str(e)}")
        raise HTTPException(status_code=500, detail="Error updating GitHub credentials.")

    finally:
        # Ensure the connection is closed properly
        cursor.close()
        conn.close()

@router.post("/validate-github/")
def validate_credentials(credentials: GitHubCredentials):
    result = validate_github_credentials(credentials.username, credentials.token)
    return {"message": result}

@router.post("/commit-and-push/")
def commit_and_push_to_github(repo_details: RepoDetails, credentials: GitHubCredentials):
    repo_url = repo_details.repo_url
    commit_message = repo_details.commit_message
    token = credentials.token  # Get token from request

    # Path to the folder containing the files to be uploaded
    folder_path = ""  # Path to the folder containing the files

    # Clone the repository if it doesn't exist locally
    repo_name = repo_url.split('/')[-1].replace('.git', '')
    repo_path = os.path.join(os.getcwd(), repo_name)

    if not os.path.exists(repo_path):
        try:
            # Modify the repo_url to include the token for authentication
            auth_repo_url = repo_url.replace("https://", f"https://{token}:x-oauth-basic@")
            repo = Repo.clone_from(auth_repo_url, repo_path)
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Error cloning repository: {e}")

    # Copy files to the cloned repo
    copy_files_to_repo(folder_path, repo_path)

    # Commit and push the changes
    commit_and_push_changes(repo_path, repo_url, commit_message, token)

    # Clean up (remove the local repo folder after push)
    shutil.rmtree(repo_path)

    return {"message": "Files successfully uploaded and committed to GitHub."}
