from fastapi import APIRouter, Depends, HTTPException, status
from fast_api.schema.request_schema import LoginRequest,UserRegister
from fast_api.services.auth_service import password_hashing,create_jwt_token
from fast_api.models.user_models import fetch_user,insert_user

router = APIRouter()

@router.post("/login")
def login(request:LoginRequest):
    useremail=request.useremail
    password=request.password
    user=fetch_user(useremail)

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, 
            detail="User not Found",
            headers={"WWW-Authenticate": "Bearer"},)
    if user.iloc[0]["USEREMAIL"] and user.iloc[0]["USERPASSWORD"]==password_hashing(password):
        token,expiry_time=create_jwt_token({"username":useremail})
        return {
            "access_token":token,
            "token_type":"bearer",
            "expiry_time":expiry_time.isoformat(),
            "useremail":useremail,
        }
    else:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, 
            detail="Invalid Credentials",
            headers={"WWW-Authenticate": "Bearer"},)

@router.post("/register")
def register(request:UserRegister):
    username=request.username
    useremail=request.email
    password=request.password
    hashed_password=password_hashing(password)
    user=fetch_user(useremail)
    print(user)
    if user is not None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, 
            detail="User Already Exists",
            headers={"WWW-Authenticate": "Bearer"},)
    else:
        insert_user(username,useremail,hashed_password)
        return {
            "message":"User Registered Successfully"
        }
        