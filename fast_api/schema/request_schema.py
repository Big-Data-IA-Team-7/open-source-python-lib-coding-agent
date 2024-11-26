from pydantic import BaseModel, Field, EmailStr
from typing import List, Optional, Dict

class LoginRequest(BaseModel):
    useremail: EmailStr = Field(..., description="The username much be uniquer and between 3 and 20 characters")
    password: str = Field(..., min_length=6, desciption="The user's password, must be at least 6 characters long")

class UserRegister(BaseModel):
    username: str = Field(..., min_length=3,max_length=20, description="The username much be uniquer and between 3 and 20 characters")
    email: EmailStr = Field(..., description="The user's email address. Must be the valid email format")
    password: str = Field(..., min_length=6, desciption="The user's password, must be at least 6 characters long")