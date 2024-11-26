import os, base64,hmac,hashlib,jwt
from fastapi import HTTPException, status, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from datetime import datetime,timedelta,timezone
from fast_api.models.user_models import fetch_user
from dotenv import load_dotenv
# Load environment variables from .env file
load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY")
security=HTTPBearer()

def password_hashing(password:str):
    """Hash the password for security."""
    seceret_key=base64.b64encode(SECRET_KEY.encode())
    hash_object = hmac.new(seceret_key, msg=password.encode(), digestmod=hashlib.sha256)
    hash_hex=hash_object.hexdigest()
    return hash_hex

def create_jwt_token(data:dict):
    """Create a JWT token."""
    expiry_time = datetime.now(timezone.utc) + timedelta(hours=1)
    token_payload = {"exp": expiry_time, **data}
    token=jwt.encode(token_payload, SECRET_KEY, algorithm="HS256")
    return token,expiry_time

def decode_jwt_token(token:str):
    try:
        decode_jwt_token=jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        return decode_jwt_token
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, 
            detail="Token has expired",
            header={"WWW-Authenticate": "Bearer"},)
    except jwt.InvalidTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, 
            detail="Invalid token",
            header={"WWW-Authenticate": "Bearer"},)
def get_current_user(credentials:HTTPAuthorizationCredentials=Depends(security)):
    """Get the current user from the JWT token."""
    token=credentials.credentials
    try:
        payload=decode_jwt_token(token)
        username=payload.get("username")
        if not username:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, 
                detail="Invalid token",
                header={"WWW-Authenticate": "Bearer"},)
        user=fetch_user(username)
        if user is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, 
                detail="User Not Found",
                header={"WWW-Authenticate": "Bearer"},)
        return user.to_dict(orient='records')[0]
    except HTTPException as e:
        return e
    
