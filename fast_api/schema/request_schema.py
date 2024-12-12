from pydantic import BaseModel, Field, EmailStr
from typing import List, Dict

class LoginRequest(BaseModel):
    username: str = Field(
        ..., 
        min_length=3,
        max_length=20,
        description="Username for authentication"
    )
    password: str = Field(
        ..., 
        min_length=6,
        max_length=100,
        description="User's password"
    )

class UserRegister(BaseModel):
    username: str = Field(
        ...,
        min_length=3,
        max_length=20,
        pattern="^[a-zA-Z0-9_-]+$", 
        description="The username must be unique and between 3 and 20 characters. Only letters, numbers, underscores and hyphens are allowed"
    )
    email: EmailStr = Field(
        ...,
        description="The user's email address. Must be in valid email format"
    )
    password: str = Field(
        ...,
        min_length=6,
        max_length=100,
        description="The user's password, must be at least 6 characters long"
    )

class HowToRequest(BaseModel):
    query: str
    history: List[Dict[str, str]] = []
    library: str

class ErrorRequest(BaseModel):
    task: str
    code: str
    error: str
    history: List[Dict[str, str]] = []
    library: str


class GitHubCredentials(BaseModel):
    username: str
    token: str

class RepoDetails(BaseModel):
    repo_url: str
    commit_message: str
    file_name: str
    code_content: str


# # Request model
# class UserLookupRequest(BaseModel):
#     useremail: str


# Request model for GitHub credential updates
class GitHubCredentialsRequest(BaseModel):
    username: str
    github_username: str
    git_token: str
    
class RepoRequest(BaseModel):
    repo_url: str
    file_name: str
    code_content: str
    commit_message: str

class AppBuildRequest(BaseModel):
    query: str
    history: List[Dict[str, str]] = []
    library: str