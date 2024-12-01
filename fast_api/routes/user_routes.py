from fastapi import APIRouter, HTTPException, status
from fast_api.schema.request_schema import LoginRequest, UserRegister
from fast_api.services.auth_service import password_hashing, create_jwt_token
from fast_api.services.user_service import fetch_user, insert_user, fetch_user_by_email

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
        print(f"Login attempt for username: {request.username}")
        
        # Input validation
        if not request.username or not request.password:
            print(f"Missing credentials - Username provided: {bool(request.username)}, Password provided: {bool(request.password)}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username and password are required",
            )
        
        # Fetch user by username
        user = fetch_user(request.username)
        print(f"User fetch result: {user is not None}")
        
        if user is None or user.empty:
            print(f"User not found or empty DataFrame for username: {request.username}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid username or password",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        # Print user data structure (excluding sensitive info)
        print(f"User data columns: {user.columns.tolist()}")
        print(f"Number of rows returned: {len(user)}")
        
        try:
            # Verify password
            stored_password = user.iloc[0]["USERPASSWORD"]
            username = user.iloc[0]["USERNAME"]
            
            # Hash the provided password for comparison
            hashed_input_password = password_hashing(request.password)
            print(f"Password verification attempt for user: {username}")
            print(f"Password hashes match: {stored_password == hashed_input_password}")
            
            if stored_password == hashed_input_password:
                print("Password verified successfully")
                token, expiry_time = create_jwt_token({"username": username})
                
                return {
                    "access_token": token,
                    "token_type": "bearer",
                    "expiry_time": expiry_time.isoformat(),
                    "username": username,
                }
            else:
                print("Password verification failed")
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid username or password",
                    headers={"WWW-Authenticate": "Bearer"},
                )
                
        except IndexError as e:
            print(f"Error accessing user data structure: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Error processing user data",
            )
            
    except HTTPException as he:
        # Re-raise HTTP exceptions
        print(f"HTTP Exception occurred: {he.detail}")
        raise he
        
    except Exception as e:
        print(f"Unexpected error during login: {str(e)}")
        print(f"Error type: {type(e).__name__}")
        # Print the full error traceback
        import traceback
        print(f"Full traceback:\n{traceback.format_exc()}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred during login. Please try again later.",
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