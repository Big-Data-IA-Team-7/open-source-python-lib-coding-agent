import snowflake.connector
from fastapi import HTTPException, status
import pandas as pd
from typing import Optional, Dict, Any
import logging

from fast_api.config.db_connection import snowflake_connection, close_connection

logger = logging.getLogger(__name__)

def fetch_user_by_email(email: str) -> Optional[pd.DataFrame]:
    """
    Fetch user data from Snowflake using email address.
    
    Args:
        email (str): Email address of the user to fetch
        
    Returns:
        Optional[pd.DataFrame]: DataFrame containing user data if found, None otherwise
        
    Raises:
        HTTPException: If database operation fails
    """
    conn = None
    cursor = None
    
    try:
        if not isinstance(email, str) or not email.strip():
            logger.error("Invalid email provided")
            raise ValueError("Invalid email provided")

        conn = snowflake_connection()
        cursor = conn.cursor()

        select_query = """
        SELECT *
        FROM USERDETAILSGITHUB
        WHERE useremail = %s
        """

        cursor.execute(select_query, (email,))
        columns = [col[0] for col in cursor.description]
        user = cursor.fetchone()

        if user:
            user_df = pd.DataFrame([user], columns=columns)
            return user_df
        return None

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except snowflake.connector.errors.ProgrammingError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Database error: {str(e)}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Unexpected error: {str(e)}"
        )
    finally:
        if cursor:
            cursor.close()
        if conn:
            close_connection(conn)

def fetch_user(username: str) -> Optional[pd.DataFrame]:
    """
    Fetch user data from Snowflake.
    
    Args:
        username (str): Username of the user to fetch
        
    Returns:
        Optional[pd.DataFrame]: DataFrame containing user data if found, None otherwise
        
    Raises:
        HTTPException: If database operation fails
    """
    conn = None
    cursor = None
    
    try:
        if not isinstance(username, str) or not username.strip():
            logger.error("Invalid username provided")
            raise ValueError("Invalid username provided")

        conn = snowflake_connection()
        cursor = conn.cursor()

        select_query = """
        SELECT *
        FROM USERDETAILSGITHUB
        WHERE username = %s
        """

        cursor.execute(select_query, (username,))
        columns = [col[0] for col in cursor.description]
        user = cursor.fetchone()

        if user:
            user_df = pd.DataFrame([user], columns=columns)
            return user_df
        return None

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except snowflake.connector.errors.ProgrammingError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Database error: {str(e)}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Unexpected error: {str(e)}"
        )
    finally:
        if cursor:
            cursor.close()
        if conn:
            close_connection(conn)

def insert_user(username: str, email: str, password: str) -> Dict[str, Any]:
    """
    Insert user data into Snowflake.
    
    Args:
        username (str): Username for the new user
        email (str): Email address for the new user
        password (str): Hashed password for the new user
        
    Returns:
        Dict[str, Any]: Success message and status
        
    Raises:
        HTTPException: If insertion fails or validation fails
    """
    conn = None
    cursor = None
    
    try:
        # Input validation
        if not all(isinstance(x, str) for x in [username, email, password]):
            raise ValueError("All inputs must be strings")
        if not all(x.strip() for x in [username, email, password]):
            raise ValueError("Empty values are not allowed")

        conn = snowflake_connection()
        cursor = conn.cursor()

        # Insert new user
        insert_query = """
        INSERT INTO USERDETAILSGITHUB (username, useremail, userpassword)
        VALUES (%s, %s, %s)
        """

        cursor.execute(insert_query, (username, email, password))
        conn.commit()

        return {
            "status": "success",
            "message": "User registered successfully",
            "username": username,
            "email": email
        }

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except snowflake.connector.errors.ProgrammingError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Database error: {str(e)}"
        )
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Unexpected error: {str(e)}"
        )
    finally:
        if cursor:
            cursor.close()
        if conn:
            close_connection(conn)
