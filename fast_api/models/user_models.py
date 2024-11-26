import snowflake.connector
from fast_api.config.db_connection import snowflake_connection
import pandas as pd


def fetch_user(useremail:str):
    """Fetch user data from Snowflake."""
    
    try:
        # Connect to Snowflake using credentials from environment variables
        conn = snowflake_connection()

        # Create a cursor object
        cursor = conn.cursor()

        # Fetch the user data from Snowflake
        select_query = """
        SELECT *
        FROM USERDETAILS
        WHERE useremail = %s
        """

        cursor.execute(select_query, (useremail,))
        columns = [col[0] for col in cursor.description]
        
        user = cursor.fetchone()

        if user:
            
            # Store the fetched data into a pandas DataFrame
            user_df = pd.DataFrame([user], columns=columns)
            return user_df
        else:
            return None
        

    except snowflake.connector.errors.ProgrammingError as e:
        print(f"Error: {e}")
    finally:
        cursor.close()
        conn.close()

def insert_user(username:str, email:str, password:str):
    """Insert user data into Snowflake."""
    try:
        # Connect to Snowflake using credentials from environment variables
        conn = snowflake_connection()

        # Create a cursor object
        cursor = conn.cursor()

        # Insert the new user data into Snowflake
        insert_query = """
        INSERT INTO USERDETAILS (username, useremail, userpassword)
        VALUES (%s, %s, %s)
        """

        cursor.execute(insert_query, (username, email, password))
        conn.commit()

        print("User credentials inserted successfully!")

    except snowflake.connector.errors.ProgrammingError as e:
        print(f"Error: {e}")
    finally:
        cursor.close()
        conn.close()
