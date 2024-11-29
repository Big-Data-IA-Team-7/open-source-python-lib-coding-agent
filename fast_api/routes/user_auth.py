from fastapi import APIRouter, Depends, HTTPException, status
from fast_api.schema.request_schema import LoginRequest,UserRegister
from fast_api.services.auth_service import password_hashing,create_jwt_token
from fast_api.services.user_service import fetch_user,insert_user, fetch_user_by_email

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

@router.post("/register", status_code=status.HTTP_201_CREATED)
async def register(request: UserRegister):
    """
    Register a new user.
    
    Args:
        request (UserRegister): Registration details containing username, email, and password
        
    Returns:
        dict: Success message and user details
        
    Raises:
        HTTPException: If registration fails or user already exists
    """
    try:
        username = request.username.strip()
        useremail = request.email.strip()
        password = request.password

        # Check if user exists by username
        user_by_username = fetch_user(username)
        if user_by_username is not None:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Username already taken",
                headers={"WWW-Authenticate": "Bearer"},
            )

        # Create separate function to check by email
        user_by_email = fetch_user_by_email(useremail)
        if user_by_email is not None:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Email already registered",
                headers={"WWW-Authenticate": "Bearer"},
            )

        # Hash password
        try:
            hashed_password = password_hashing(password)
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Error processing password"
            )

        # Insert new user
        try:
            result = insert_user(username, useremail, hashed_password)
            
            return {
                "status": "success",
                "message": "User registered successfully",
                "username": username,
                "email": useremail
            }
            
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to register user"
            )

    except HTTPException as e:
        raise e
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Registration failed: {str(e)}"
        )