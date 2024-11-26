from fastapi import APIRouter, Depends, HTTPException, status
from fast_api.schema.request_schema import LoginRequest,UserRegister
from fast_api.services.auth_service import password_hashing,create_jwt_token
from fast_api.models.user_models import fetch_user,insert_user

router = APIRouter()

@router.post("/login")
def login(request: LoginRequest):
    """
    Authenticate user and generate JWT token.
    
    Args:
        request (LoginRequest): Login credentials containing username and password
        
    Returns:
        dict: Authentication token and user details
        
    Raises:
        HTTPException: If authentication fails
    """
    try:
        username = request.username  # Changed from useremail
        password = request.password
        
        # Fetch user by username
        user = fetch_user(username)  # You'll need to update fetch_user to query by username
        
        if user is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found",
                headers={"WWW-Authenticate": "Bearer"},
            )
            
        # Verify password
        stored_password = user.iloc[0]["USERPASSWORD"]
        if user.iloc[0]["USERNAME"] and stored_password == password_hashing(password):
            token, expiry_time = create_jwt_token({"username": username})
            
            return {
                "access_token": token,
                "token_type": "bearer",
                "expiry_time": expiry_time.isoformat(),
                "username": username,
            }
        else:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )
            
    except IndexError:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error accessing user data",
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Login failed: {str(e)}",
        )

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
        