from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel
from git import Repo
import os
import shutil
from fast_api.schema.request_schema import RepoRequest

router = APIRouter()

@router.post("/process-repo/")
async def process_repo(request: RepoRequest):
    local_repo_path = os.path.join(os.getcwd(), request.repo_url.split("/")[-1].replace(".git", ""))

    try:
        # Step 1: Clone or pull the repository
        if not os.path.exists(local_repo_path):
            Repo.clone_from(request.repo_url, local_repo_path)
            clone_status = f"Repository cloned to {local_repo_path}"
        else:
            repo = Repo(local_repo_path)
            origin = repo.remote(name="origin")
            origin.pull()
            clone_status = f"Repository updated at {local_repo_path}"

        # Step 2: Write the code to a file
        file_path = os.path.join(local_repo_path, request.file_name)
        with open(file_path, "w") as file:
            file.write(request.code_content)

        # Step 3: Commit and push changes
        repo = Repo(local_repo_path)
        repo.git.add(A=True)
        repo.index.commit(request.commit_message)
        repo.remote(name="origin").push()
        commit_status = "Changes committed and pushed successfully!"

        # Step 4: Cleanup
        shutil.rmtree(local_repo_path)
        cleanup_status = f"Local repository at {local_repo_path} deleted successfully."

        return {
            "clone_status": clone_status,
            "commit_status": commit_status,
            "cleanup_status": cleanup_status,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
