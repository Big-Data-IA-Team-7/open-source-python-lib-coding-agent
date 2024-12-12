from fastapi import APIRouter, HTTPException
from git import Repo
import os
from fast_api.schema.request_schema import GitHubCredentials, RepoDetails, GitHubCredentialsRequest
from fast_api.services.github_service import validate_github_credentials, commit_and_push
from fast_api.config.db_connection import snowflake_connection
import logging

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
def commit_and_push_code(repo_details: RepoDetails, credentials: GitHubCredentials):
    repo_owner = repo_details.repo_url.split('/')[3]
    repo_path = os.path.join(os.getcwd(), repo_details.repo_url.split('/')[-1].replace(".git", ""))
    
    # Clone the repository if it doesn't exist locally
    if not os.path.exists(repo_path):
        try:
            repo = Repo.clone_from(repo_details.repo_url, repo_path, env={"GIT_ASKPASS": "echo", "GIT_USERNAME": credentials.username, "GIT_PASSWORD": credentials.token})
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Error cloning repository: {e}")
    
    # Call the commit and push function
    result = commit_and_push(repo_path, repo_details.commit_message, credentials.username, credentials.token, repo_owner, repo_details.file_name, repo_details.code_content)
    return {"message": result}